
from typing import Any
from qiskit import transpile
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_ibm_runtime import SamplerV2 as Sampler
from qiskit import QuantumCircuit

def run_counts(backend, circuit, shots=4096):
    sampler = Sampler(mode=backend)
    job = sampler.run([circuit], shots=shots)
    result = job.result()
    cr = list(result[0].data.keys())
    if len(cr) != 1:
        raise ValueError(f"Expected exactly one circuit result, got {len(cr)}")
    counts = result[0].data[cr[0]].get_counts()
    return counts

def transpile_and_run_counts(backend, circuit, shots=4096):
    tqc = transpile(circuit, backend)
    return run_counts(backend, tqc, shots)



def optimize_circuit(
    circuit: Any,
    backend: Any,
    optimization_level: int = 1,
):
    """
    Transpile a quantum circuit for a backend.

    Args:
        circuit:
            Quantum circuit to transpile.
        backend:
            Real, fake, or simulated backend whose target should be used.
        optimization_level:
            Qiskit transpiler optimization level from 0 to 3.

    Returns:
        The transpiled circuit.
    """
    if optimization_level not in {0, 1, 2, 3}:
        raise ValueError(
            "optimization_level must be 0, 1, 2, or 3."
        )

    pass_manager = generate_preset_pass_manager(
        backend=backend,
        optimization_level=optimization_level,
    )

    return pass_manager.run(circuit)


def run_sampler(
    circuit: Any,
    backend: Any,
    shots: int = 4096,
):
    """
    Execute a circuit with SamplerV2 and return measurement counts.

    Args:
        circuit:
            Transpiled circuit containing measurements.
        backend:
            Backend or AerSimulator used for execution.
        shots:
            Number of circuit repetitions.

    Returns:
        A tuple containing:

        - Measurement counts
        - Primitive result
        - Submitted job
    """
    if shots <= 0:
        raise ValueError("shots must be greater than zero.")

    sampler = Sampler(mode=backend)

    job = sampler.run(
        [circuit],
        shots=shots,
    )

    result = job.result()
    pub_result = result[0]

    register_names = list(pub_result.data.keys())

    if not register_names:
        raise ValueError(
            "No classical measurement register was found. "
            "Make sure the circuit contains measurements."
        )

    register_name = register_names[0]
    counts = pub_result.data[register_name].get_counts()

    return counts, result, job


def transpile_with_layout(
    circuit: QuantumCircuit,
    backend: Any,
    initial_layout: list[int],
    optimization_level: int = 3,
    seed_transpiler: int | None = None,
) -> QuantumCircuit:
    """
    Transpile a circuit for a backend using a specified initial layout.

    Args:
        circuit:
            Circuit to transpile.
        backend:
            Real, fake or simulated backend.
        initial_layout:
            Physical qubits assigned to the circuit's virtual qubits.
        optimization_level:
            Transpiler optimization level from 0 to 3.
        seed_transpiler:
            Optional seed for reproducible transpilation.

    Returns:
        The transpiled circuit.
    """
    if len(initial_layout) != circuit.num_qubits:
        raise ValueError(
            "The initial layout must contain one physical-qubit "
            "index for every circuit qubit."
        )

    if optimization_level not in {0, 1, 2, 3}:
        raise ValueError(
            "optimization_level must be 0, 1, 2, or 3."
        )

    pass_manager = generate_preset_pass_manager(
        backend=backend,
        initial_layout=initial_layout,
        optimization_level=optimization_level,
        seed_transpiler=seed_transpiler,
    )

    return pass_manager.run(circuit)