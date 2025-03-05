# The motivation behind bound-motivation is, that some solvers can experience numerical 
# instabilities with very small values

from math import exp, sqrt
import numpy as np

from termination.variance_based.exponent_approximation.inductive_bound import _compute_b


def validate_bound(values, quantiles, epsilon, d, sg_cutoff, C, d_0, delta1):
    assert len(values) ==len(quantiles)

    b = _compute_b(epsilon, d, C)
    sg_value = exp(-C*(sg_cutoff-b*(sqrt(1+d)/(sqrt(1+d)-1))-delta1)/2)
    last_quantile = 1-sg_value-quantiles[-1]
    assert last_quantile > 0

    values_prime = np.append(values, sg_cutoff)
    quantiles_prime = np.append(values, sg_cutoff)

    new_quantiles = np.zeros(len(quantiles))