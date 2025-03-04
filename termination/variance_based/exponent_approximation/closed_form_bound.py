from math import log, pow


def get_closed_form_bound_asymptotic(degree, C):
    nom = log(0.836)
    denom = log(pow(((3.55/C+1.95)**2)*0.71/(5.5**2) + 1, 1/degree))
    return nom/denom