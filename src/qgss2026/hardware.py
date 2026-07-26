

import pandas as pd
import numpy as np
from __future__ import annotations
from typing import Any, Iterable


def _safe_value(function, *args):
    """Call a backend-property function without crashing on missing data."""
    try:
        value = function(*args)

        if value is None:
            return None

        return value

    except (KeyError, TypeError, ValueError):
        return None

    except Exception:
        return None


def backend_summary(
    backend: Any,
    max_rows: int = 8,
    single_qubit_gates: Iterable[str] | None = None,
    two_qubit_gates: Iterable[str] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Create summary tables for qubit and two-qubit gate properties.

    Args:
        backend:
            An IBM Quantum backend.
        max_rows:
            Maximum number of qubits to include in the qubit table.
        single_qubit_gates:
            Single-qubit gates whose errors should be displayed.
        two_qubit_gates:
            Two-qubit gates whose errors should be displayed.

    Returns:
        A tuple containing:

        - A DataFrame with T1, T2, readout error and single-qubit errors.
        - A DataFrame with two-qubit gate errors.
    """
    props = backend.properties()

    qubit_rows: list[dict[str, Any]] = []

    number_of_rows = min(backend.num_qubits, max_rows)

    for qubit in range(number_of_rows):
        t1 = (
            _safe_value(props.t1, qubit)
            if props is not None
            else None
        )

        t2 = (
            _safe_value(props.t2, qubit)
            if props is not None
            else None
        )

        readout_error = (
            _safe_value(props.readout_error, qubit)
            if props is not None
            else None
        )

        row: dict[str, Any] = {
            "qubit": qubit,
            "T1 (us)": None if t1 is None else round(t1 * 1e6, 2),
            "T2 (us)": None if t2 is None else round(t2 * 1e6, 2),
            "readout_error": (
                None
                if readout_error is None
                else round(readout_error, 5)
            ),
        }

        if single_qubit_gates is not None and props is not None:
            for gate in single_qubit_gates:
                error = _safe_value(
                    props.gate_error,
                    gate,
                    [qubit],
                )

                row[f"{gate} error"] = (
                    None if error is None else round(error, 5)
                )

        qubit_rows.append(row)

    coupling_rows: list[dict[str, Any]] = []

    if (
        two_qubit_gates is not None
        and props is not None
        and backend.coupling_map is not None
    ):
        coupling_edges = backend.coupling_map.get_edges()

        for gate in two_qubit_gates:
            for qubit1, qubit2 in coupling_edges:
                error = _safe_value(
                    props.gate_error,
                    gate,
                    [qubit1, qubit2],
                )

                # Only include edges where this gate has calibration data.
                if error is not None:
                    coupling_rows.append(
                        {
                            "gate": gate,
                            "qubit1": qubit1,
                            "qubit2": qubit2,
                            "gate_error": round(error, 5),
                        }
                    )

    return (
        pd.DataFrame(qubit_rows),
        pd.DataFrame(coupling_rows),
    )


def get_backend_information(
    service: Any,
    backend_name: str = "ibm_fez",
) -> tuple[Any, list[str], list[tuple[int, int]]]:
    """
    Load an IBM Quantum backend and retrieve its basic hardware information.

    Args:
        service:
            An initialized QiskitRuntimeService instance.
        backend_name:
            IBM Quantum backend name. The default is ``ibm_fez``.

    Returns:
        A tuple containing:

        - backend: The loaded backend object.
        - basis_operations: Operations supported by the backend.
        - coupling_map: Directly connected physical-qubit pairs.
    """
    backend = service.backend(backend_name)

    basis_operations = list(backend.operation_names)

    coupling_map = (
        list(backend.coupling_map.get_edges())
        if backend.coupling_map is not None
        else []
    )

    return backend, basis_operations, coupling_map

def backend_summary_detail(backend):
    conf = backend.configuration()
    props = backend.properties()
    n_qubits = backend.num_qubits

    # T1/T2/readout from BackendProperties.
    t1s, t2s, readout_errs = [], [], []
    for q in range(n_qubits):
        t1s.append(props.t1(q))
        t2s.append(props.t2(q))
        readout_errs.append(props.readout_error(q))
    
    gate_errs = dict()
    for gate in conf.gates:
        gate = gate.to_dict()
        if (gate["name"] in ["reset", "measure", "rz"]): # "rz" has no error
            continue
        for applied_qubits in gate["coupling_map"]:
            applied_qubits = tuple(applied_qubits)
            if applied_qubits not in gate_errs:
                gate_errs[applied_qubits] = list()
            gate_errs[applied_qubits].append(props.gate_error(gate["name"], applied_qubits))

    twoq_errs, oneq_errs = list(), list()
    for qubits, err in gate_errs.items():
        if len(qubits) == 1:
            oneq_errs.append(err)
        elif len(qubits) == 2:
            twoq_errs.append(err)
        else:
            raise Exception

    if n_qubits < 10:
        size_family = "small: <10 qubits"
    elif n_qubits < 120:
        size_family = "medium: <120 qubits"
    else:
        size_family = "large: >=120 qubits"

    return {
        "name": backend.name,
        "date": backend.online_date,
        "n_qubits": n_qubits,
        "n_coupling_edges": len(backend.coupling_map.get_edges())//2,
        "t1_median_us": np.median(t1s) * 1e6,
        "t2_median_us": np.median(t2s) * 1e6,
        "readout_error_median": np.median(readout_errs),
        "oneq_error_median": np.median(oneq_errs),
        "twoq_error_median": np.median(twoq_errs),
        "size_family": size_family
    }


def get_least_busy_dynamic_backend(
    service: Any,
    min_num_qubits: int = 12,
):
    """
    Select the least-busy operational QPU that supports dynamic circuits.

    Args:
        service:
            An initialized QiskitRuntimeService.
        min_num_qubits:
            Minimum number of qubits required.

    Returns:
        The selected IBM Quantum backend.
    """
    if not isinstance(min_num_qubits, int) or min_num_qubits < 1:
        raise ValueError(
            "min_num_qubits must be a positive integer."
        )

    return service.least_busy(
        operational=True,
        simulator=False,
        min_num_qubits=min_num_qubits,
        dynamic_circuits=True,
    )
