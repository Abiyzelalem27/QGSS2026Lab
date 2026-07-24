

from qiskit import QuantumCircuit

def ghz_fan(n: int) -> QuantumCircuit:
    """Create an n-qubit GHZ circuit using fan-out CNOT gates."""
    qc = QuantumCircuit(n)
    qc.h(0)

    for i in range(1, n):
        qc.cx(0, i)

    return qc


def ghz_chain(n: int) -> QuantumCircuit:
    """Create an n-qubit GHZ circuit using chained CNOT gates."""
    qc = QuantumCircuit(n)
    qc.h(0)

    for i in range(n - 1):
        qc.cx(i, i + 1)

    return qc 

def ghz_half_depth(n, add_barriers=False):
    """GHZ starting from the middle, growing outward in both directions.

    Pass add_barriers=True to insert a barrier after each outward step; this
    makes the parallel layers visible in the circuit drawing. Barriers count
    as a layer, so always measure depth on a barrier-free circuit.
    """
    qc = QuantumCircuit(n)
    mid = n // 2
    qc.h(mid)

    # Spread left and right simultaneously
    for step in range(1, n):
        left = mid - step
        right = mid + step
        if left >= 0:
            qc.cx(left + 1, left)  # Spread left
        if add_barriers:
            qc.barrier()
        if right < n:
            qc.cx(right - 1, right)  # Spread right
        if left <= 0 and right >= n - 1:
            break
    return qc