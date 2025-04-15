from math import exp, log, sqrt, pow
import sys
import numpy as np
from scipy.stats import norm

from termination.variance_based.variance_bound_witness import VarianceBoundWitness


def _calculate_percentage_of_terminating(self, t, d, C, delta1, delta2, c_0):
    left_lower_bound = 1 - exp(
        C * (-((t - 1 - delta2) ** 2)) / (2 * (d * delta1 / (d * delta1 - 1)) ** 2)
    )
    left_lower_bound2 = norm.cdf(-(t) / sqrt(d * delta1 - 1)) - c_0
    union_bound = left_lower_bound * left_lower_bound2
    return union_bound


def estimate_bound_percentage_of_terminating_union_bound(
    self, m, C, delta1, delta2, epsilon, c_0, n_0
):
    # TODO: This numeric approximation is very naive
    k_min = None
    perc_min = None
    t_min = None
    exp_min = 0
    for k in np.linspace(pow(6.87, 1 / (2 * m + 1)), 20, 1000):
        for t in np.linspace(2, 30, 100):
            perc = 1 - self._calculate_percentage_of_terminating(
                t, pow(k, (2 * m + 1)), C, delta1, delta2, c_0
            )
            exp = log(perc) / log(k + epsilon)
            if perc >= 0.999:
                continue
            if exp < exp_min:
                t_min = t
                perc_min = perc
                k_min = k
                exp_min = exp

    return VarianceBoundWitness(
        epsilon, delta1, delta2, m, t_min, k_min, exp_min, perc_min, n_0
    )


def _estimate_needed_exponent(self, C, delta1, delta2, c_0):  #
    # This function computes the minimum exponent, rather than computing the bound when given an exponent
    k_min = None
    perc_min = None
    m_min = sys.maxsize
    t_min = None
    d_min = None
    for d in np.linspace(6.87, 10000, 10000):
        for t in np.linspace(2, 50, 100):
            perc = 1 - self._calculate_percentage_of_terminating(
                t, d, C, delta1, delta2, c_0
            )
            if perc >= 0.999:
                continue
            k_upper_bound = 1 / perc
            required_m = (log(d + 1) / log(k_upper_bound) - 1) / 2
            if m_min > required_m:
                t_min = t
                d_min = d
                m_min = required_m
                perc_min = perc
                k_min = k_upper_bound

    exponent_min = log(perc_min) / log(k_min)
    return exponent_min
