



from __future__ import annotations
from typing import Any
from qiskit_aer import AerSimulator

from qiskit_aer.noise import (
    NoiseModel,
    ReadoutError,
    depolarizing_error,
    thermal_relaxation_error,
)




def depol_x_simulator(lam):
    """Create a simulator with depolarizing noise on every X gate."""
    noise_model = NoiseModel()

    error = depolarizing_error(lam, 1)
    noise_model.add_all_qubit_quantum_error(error, "x")

    return AerSimulator(noise_model=noise_model) 


def create_backend_informed_simulator(
    backend: Any,
) -> AerSimulator:
    """
    Create a noisy Aer simulator using information from a backend.

    The backend can be a real IBM Quantum backend or a fake backend.

    Args:
        backend:
            Real or fake Qiskit backend containing device properties.

    Returns:
        An AerSimulator configured using the backend's noise properties,
        basis gates and coupling map.
    """
    return AerSimulator.from_backend(backend)


def create_custom_noisy_simulator(
    lam_1q: float = 0.003,
    lam_2q: float = 0.03,
    p_readout: float = 0.015,
    coupling_map: list[list[int]] | None = None,
) -> tuple[AerSimulator, NoiseModel]:
    """
    Create a five-qubit simulator with a custom noise model.

    Args:
        lam_1q:
            Depolarizing-error strength for noisy single-qubit gates.
        lam_2q:
            Depolarizing-error strength for two-qubit gates.
        p_readout:
            Symmetric measurement-error probability.
        coupling_map:
            Optional custom qubit connectivity. By default, a bidirectional
            five-qubit linear coupling map is used.

    Returns:
        A tuple containing:

        - The configured AerSimulator.
        - The custom NoiseModel.
    """
    for parameter_name, value in {
        "lam_1q": lam_1q,
        "lam_2q": lam_2q,
        "p_readout": p_readout,
    }.items():
        if not 0 <= value <= 1:
            raise ValueError(
                f"{parameter_name} must be between 0 and 1."
            )

    # Gates affected by noise
    single_qubit_gates_noisy = ["sx", "x"]
    two_qubit_gates_noisy = ["cx"]

    # RZ is treated as ideal in this model.
    basis_gates = [
        "rz",
        *single_qubit_gates_noisy,
        *two_qubit_gates_noisy,
    ]

    if coupling_map is None:
        coupling_map = [
            [0, 1],
            [1, 2],
            [2, 3],
            [3, 4],
            [1, 0],
            [2, 1],
            [3, 2],
            [4, 3],
        ]

    noise_model = NoiseModel(basis_gates=basis_gates)

    # Single-qubit depolarizing noise
    single_qubit_error = depolarizing_error(
        lam_1q,
        num_qubits=1,
    )

    noise_model.add_all_qubit_quantum_error(
        single_qubit_error,
        single_qubit_gates_noisy,
    )

    # Two-qubit depolarizing noise
    two_qubit_error = depolarizing_error(
        lam_2q,
        num_qubits=2,
    )

    noise_model.add_all_qubit_quantum_error(
        two_qubit_error,
        two_qubit_gates_noisy,
    )

    # Symmetric readout noise
    readout_error = ReadoutError(
        [
            [1 - p_readout, p_readout],
            [p_readout, 1 - p_readout],
        ]
    )

    noise_model.add_all_qubit_readout_error(readout_error)

    simulator = AerSimulator(
        noise_model=noise_model,
        basis_gates=basis_gates,
        coupling_map=coupling_map,
    )

    return simulator, noise_model


def create_t1_delay_simulator(
    delay_ns: float,
    t1_us: float = 60.0,
    t2_us: float = 40.0,
) -> AerSimulator:
    """
    Create a simulator with thermal relaxation applied to delay operations.

    Args:
        delay_ns:
            Duration of the delay operation in nanoseconds.
        t1_us:
            T1 relaxation time in microseconds.
        t2_us:
            T2 coherence time in microseconds.

    Returns:
        AerSimulator configured with a thermal-relaxation noise model.
    """
    if delay_ns < 0:
        raise ValueError("delay_ns must be non-negative.")

    if t1_us <= 0 or t2_us <= 0:
        raise ValueError("T1 and T2 must be greater than zero.")

    if t2_us > 2 * t1_us:
        raise ValueError("T2 must satisfy T2 <= 2 * T1.")

    # Convert microseconds to nanoseconds.
    t1_ns = t1_us * 1_000
    t2_ns = t2_us * 1_000

    relaxation_error = thermal_relaxation_error(
        t1=t1_ns,
        t2=t2_ns,
        time=delay_ns,
    )

    noise_model = NoiseModel()
    noise_model.add_all_qubit_quantum_error(
        relaxation_error,
        ["delay"],
    )

    return AerSimulator(noise_model=noise_model) 