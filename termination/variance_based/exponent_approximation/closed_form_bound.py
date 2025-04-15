from math import log, pow, sqrt


def get_closed_form_bound_asymptotic(degree, C):
    nom = log(0.836)
    denom = log(pow(((3.55 / C + 1.95) ** 2) * 0.71 / (5.5**2) + 1, 1 / degree))
    return nom / denom


def _get_c_d_prime(C):
    c_prime = (5.5 - 1.95) / sqrt(C) + 1.95
    d_prime = (c_prime * sqrt(0.71) / 5.5) ** 2
    return c_prime, d_prime
