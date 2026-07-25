
from typing import Mapping

import pandas as pd



def ghz_success_probability(
    counts: dict[str, int],
    n: int,
) -> float:
    """Return the probability of measuring all zeros or all ones."""
    total = sum(counts.values())

    if total == 0:
        raise ValueError("The counts dictionary contains no shots.")

    all_zeros = "0" * n
    all_ones = "1" * n

    successful = (
        counts.get(all_zeros, 0)
        + counts.get(all_ones, 0)
    )

    return successful / total 

def prob_of_zero(counts, nbits=1):
    key = "0" * nbits
    return counts.get(key, 0) / sum(counts.values()) 

def depol_survival_model(n, lam):
    """Return the expected survival probability after 2n noisy X gates."""
    return 0.5 + 0.5 * (1 - lam) ** (2 * n) 

"""Result-analysis utilities for QGSS 2026."""

def compare_count_distributions(
    ideal_counts: Mapping[str, int],
    noisy_counts: Mapping[str, int],
) -> pd.DataFrame:
    """
    Compare ideal and noisy measurement-count distributions.

    Args:
        ideal_counts:
            Counts returned by the ideal simulator.
        noisy_counts:
            Counts returned by the noisy simulator.

    Returns:
        DataFrame containing counts and probabilities for every bitstring.
    """
    ideal_shots = sum(ideal_counts.values())
    noisy_shots = sum(noisy_counts.values())

    if ideal_shots == 0 or noisy_shots == 0:
        raise ValueError("The count dictionaries must not be empty.")

    bitstrings = sorted(
        set(ideal_counts) | set(noisy_counts)
    )

    rows = []

    for bitstring in bitstrings:
        ideal_value = ideal_counts.get(bitstring, 0)
        noisy_value = noisy_counts.get(bitstring, 0)

        rows.append(
            {
                "bitstring": bitstring,
                "ideal_counts": ideal_value,
                "ideal_probability": ideal_value / ideal_shots,
                "noisy_counts": noisy_value,
                "noisy_probability": noisy_value / noisy_shots,
            }
        )

    dataframe = pd.DataFrame(rows)

    return dataframe.sort_values(
        by="noisy_probability",
        ascending=False,
        ignore_index=True,
    )


