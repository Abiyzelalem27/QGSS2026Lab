

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