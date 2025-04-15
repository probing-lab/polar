# The motivation behind bound-motivation is, that some solvers can experience numerical
# instabilities with very small values

from itertools import pairwise
from math import exp, sqrt
import numpy as np
from scipy.stats import norm

from termination.variance_based.exponent_approximation.inductive_bound import _compute_b

ERR = 10e-14


def validate_bound(
    values: np.ndarray,
    quantiles: np.ndarray,
    epsilon: float,
    d: float,
    sg_cutoff: float,
    C: float,
    c_0: float,
    delta1: float,
):
    assert len(values) == len(quantiles)
    assert d > 0
    assert epsilon > 0 and epsilon < 1

    b = _compute_b(epsilon, d, C)
    sg_value = exp(
        -C * (sg_cutoff - delta1 * (sqrt(1 + d) / (sqrt(1 + d))) - b) ** 2 / 2
    )
    last_quantile = 1 - sg_value
    assert last_quantile > 0

    values_prime = np.append(values, sg_cutoff)
    quantiles_prime = np.append(quantiles, last_quantile)

    densities = (
        np.array(
            [quantiles_prime[0] - epsilon]
            + [y - x for x, y in pairwise(quantiles_prime)]
        )
    ) / (1 - epsilon)

    new_bounds = []
    initial_bounds = []
    for value, target_quantile in zip(values, quantiles):
        new_value = value * sqrt(1 + d)

        probs = norm.cdf((new_value - values_prime) / sqrt(d)) - c_0

        new_quantile = np.sum(probs * densities)
        new_bounds.append(new_quantile)
        initial_bounds.append(norm.cdf(value))

    inductive_valid = np.all(np.array(new_bounds) - quantiles) > ERR
    initial_valid = np.all(np.array(initial_bounds) - quantiles) > ERR

    return inductive_valid, initial_valid
