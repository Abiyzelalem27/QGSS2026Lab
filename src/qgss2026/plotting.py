

from collections.abc import Mapping
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from qiskit import QuantumCircuit
from .circuits import quantum_circuit_params


def plot_circuit_comparison(circuits_dict, figsize=(14, 6)):
    QISKIT_COLORS = [
        '#6929C4',  # Purple (primary Qiskit color)
        '#1192E8',  # Blue
    ]
    # Extract parameters for all circuits
    all_params = {}
    for name, circuit in circuits_dict.items():
        all_params[name] = quantum_circuit_params(circuit)
    
    # Prepare data for plotting
    circuit_names = list(all_params.keys())
    metrics = ["Number of qubits", "Depth", "2-qubit depth"]
    
    # Create subplots (1 row, 4 columns)
    fig, axes = plt.subplots(1, 4, figsize=figsize)
    fig.suptitle('Quantum Circuit Parameters Comparison', fontsize=16, fontweight='bold')
    
    # Use Qiskit colors
    colors = [QISKIT_COLORS[i % len(QISKIT_COLORS)] for i in range(len(circuit_names))]
    
    # Plot each metric in first 3 subplots
    for idx, metric in enumerate(metrics):
        ax = axes[idx]
        values = [all_params[name][metric] for name in circuit_names]
        
        bars = ax.bar(range(len(circuit_names)), values, color=colors, 
                      edgecolor='#000000', linewidth=1.5, alpha=0.85)
        
        ax.set_xlabel('Circuits', fontsize=11, fontweight='bold')
        ax.set_ylabel(metric, fontsize=11, fontweight='bold')
        ax.set_title(metric, fontsize=12, fontweight='bold', pad=10)
        ax.set_xticks(range(len(circuit_names)))
        ax.set_xticklabels(circuit_names, rotation=45, ha='right')
        ax.grid(axis='y', alpha=0.3, linestyle='--', color='#CCCCCC')
        ax.set_facecolor('#F7F7F7')
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # Gate operations comparison (last subplot)
    ax = axes[3]
    gate_types = set()
    for params in all_params.values():
        if isinstance(params["Gates"], dict):
            gate_types.update(params["Gates"].keys())
    
    if gate_types:
        gate_types = sorted(gate_types)
        x = np.arange(len(gate_types))
        width = 0.8 / len(circuit_names)
        
        for i, name in enumerate(circuit_names):
            gates = all_params[name]["Gates"]
            counts = [gates.get(gate, 0) for gate in gate_types]
            offset = (i - len(circuit_names)/2) * width + width/2
            ax.bar(x + offset, counts, width, label=name, 
                   color=colors[i], edgecolor='#000000', linewidth=1, alpha=0.85)
        
        ax.set_xlabel('Gate Types', fontsize=11, fontweight='bold')
        ax.set_ylabel('Count', fontsize=11, fontweight='bold')
        ax.set_title('Gate Operations Breakdown', fontsize=12, fontweight='bold', pad=10)
        ax.set_xticks(x)
        ax.set_xticklabels(gate_types, rotation=45, ha='right')
        ax.legend(fontsize=9, framealpha=0.9)
        ax.grid(axis='y', alpha=0.3, linestyle='--', color='#CCCCCC')
        ax.set_facecolor('#F7F7F7')
    else:
        ax.text(0.5, 0.5, 'No gate data available', 
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.axis('off')
    
    plt.tight_layout()
    return fig

