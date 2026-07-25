


from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.circuit.classical import expr 

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

def repeated_x_circuit(n):
    qc = QuantumCircuit(1, 1)

    for _ in range(2 * n):
        qc.x(0)

    qc.measure(0, 0)

    return qc 

def repeated_x_meas_x_circuit(n):
    qc = QuantumCircuit(1, 1)

    # Prepare the |+> state
    qc.h(0)

    # Apply 2n X gates
    for _ in range(2 * n):
        qc.x(0)

    # Rotate back from the X basis
    qc.h(0)

    # Measure
    qc.measure(0, 0)

    return qc 

def t1_delay_circuit(delay_dt):
    """
    Create a circuit for measuring T1 population decay.

    The qubit is prepared in |1>, allowed to relax for the specified
    delay, and then measured in the computational basis.

    Args:
        delay_ns:
            Delay duration in nanoseconds.

    Returns:
        A single-qubit measurement circuit.
    """
    qc = QuantumCircuit(1, 1)
    qc.x(0)
    qc.delay(delay_dt, 0, unit="ns")
    qc.measure(0, 0)
    return qc

def t2_delay_circuit(delay_dt):
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.delay(delay_dt, 0, unit="ns")
    qc.h(0)
    qc.measure(0, 0)
    return qc 


def dynamic_ghz_circuit(num_qubits: int) -> QuantumCircuit:
    """
    Build a dynamic GHZ circuit using mid-circuit measurements
    and classical feedforward operations.

    Args:
        num_qubits: Number of qubits. Must be at least 2.

    Returns:
        A QuantumCircuit implementing the dynamic GHZ protocol.
    """
    if not isinstance(num_qubits, int) or num_qubits < 2:
        raise ValueError("num_qubits must be an integer >= 2.")

    qr = QuantumRegister(num_qubits, name="q")
    cr = ClassicalRegister(num_qubits, name="c")
    qc = QuantumCircuit(qr, cr)

    _apply_initial_hadamards(qc, num_qubits)
    _apply_first_cnot_layer(qc, num_qubits)
    _apply_second_cnot_layer(qc, num_qubits)
    _apply_dynamic_section(qc, qr, cr, num_qubits)
    _apply_final_cnot_layer(qc, num_qubits)

    qc.measure(qr, cr)

    return qc


def _apply_initial_hadamards(
    qc: QuantumCircuit,
    num_qubits: int,
) -> None:
    """Apply Hadamard gates to all even-indexed qubits."""
    for qubit in range(0, num_qubits, 2):
        qc.h(qubit)


def _apply_first_cnot_layer(
    qc: QuantumCircuit,
    num_qubits: int,
) -> None:
    """
    Apply CNOT gates from each even qubit to the preceding odd qubit.

    Examples:
        CX(2, 1), CX(4, 3), CX(6, 5), ...
    """
    for control in range(2, num_qubits, 2):
        qc.cx(control, control - 1)


def _apply_second_cnot_layer(
    qc: QuantumCircuit,
    num_qubits: int,
) -> None:
    """
    Apply CNOT gates from each even qubit to the following odd qubit.

    Examples:
        CX(0, 1), CX(2, 3), CX(4, 5), ...
    """
    for control in range(0, num_qubits - 1, 2):
        qc.cx(control, control + 1)


def _apply_dynamic_section(
    qc: QuantumCircuit,
    qr: QuantumRegister,
    cr: ClassicalRegister,
    num_qubits: int,
) -> None:
    """
    Measure bridge qubits, reset them and apply feedforward corrections.

    For an even number of qubits, the final odd-indexed boundary qubit
    is measured and reset without a correction.
    """
    # Measure the odd bridge qubits.
    for meas_qubit in range(1, num_qubits - 1, 2):
        # Usually correct the next even–odd pair.
        # For an odd-sized circuit, the last bridge may have only
        # one target qubit available.
        x_targets = list(
            range(
                meas_qubit + 1,
                min(meas_qubit + 3, num_qubits),
            )
        )

        _measure_reset_and_correct(
            qc=qc,
            qr=qr,
            cr=cr,
            meas_qubit=meas_qubit,
            x_targets=x_targets,
        )

    # With an even number of qubits, the final qubit is an odd
    # boundary qubit rather than another bridge.
    if num_qubits % 2 == 0:
        _measure_and_reset_only(
            qc=qc,
            qr=qr,
            cr=cr,
            qubit=num_qubits - 1,
        )


def _apply_final_cnot_layer(
    qc: QuantumCircuit,
    num_qubits: int,
) -> None:
    """
    Apply the final CNOT layer.

    This has the same connectivity pattern as the second CNOT layer.
    """
    for control in range(0, num_qubits - 1, 2):
        qc.cx(control, control + 1)


def _measure_reset_and_correct(
    qc: QuantumCircuit,
    qr: QuantumRegister,
    cr: ClassicalRegister,
    meas_qubit: int,
    x_targets: list[int],
) -> None:
    """
    Measure a bridge qubit into cr[0], reset it and conditionally
    apply X gates when the measurement result is 1.
    """
    qc.measure(qr[meas_qubit], cr[0])
    qc.reset(qr[meas_qubit])

    condition = expr.lift(cr[0])

    with qc.if_test(condition):
        for target in x_targets:
            qc.x(qr[target])


def _measure_and_reset_only(
    qc: QuantumCircuit,
    qr: QuantumRegister,
    cr: ClassicalRegister,
    qubit: int,
) -> None:
    """Measure a boundary qubit into cr[0] and reset it."""
    qc.measure(qr[qubit], cr[0])
    qc.reset(qr[qubit])

def quantum_circuit_params(circuit: QuantumCircuit) -> dict:
    """
    Extract key parameters from a QuantumCircuit.

    Args:
        circuit: The QuantumCircuit to analyze.

    Returns:
        A dictionary containing circuit size and depth information.
    """
    depth = circuit.depth()

    depth_2q = circuit.depth(
        lambda instruction: len(instruction.qubits) == 2
    )

    num_multi_qubit_ops = circuit.num_nonlocal_gates()
    ops = circuit.count_ops()
    num_qubits = circuit.num_qubits
    num_ancillas = circuit.num_ancillas

    return {
        "Number of qubits": num_qubits,
        "Depth": depth,
        "2-qubit depth": depth_2q,
        "Gates": ops,
        "Multi-qubit gates": num_multi_qubit_ops,
        "Number of ancillas": num_ancillas,
    }



