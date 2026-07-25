

"""Quantum-circuit operator utilities."""

from qiskit import QuantumCircuit


def count_swap_gates(circuit: QuantumCircuit) -> int:
    """
    Count the number of SWAP gates in a circuit.

    Args:
        circuit: The QuantumCircuit to analyze.

    Returns:
        The number of SWAP gates in the circuit.
    """
    swap_count = 0

    for instruction in circuit.data:
        if instruction.operation.name == "swap":
            swap_count += 1

    return swap_count 