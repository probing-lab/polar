from sympy import expand, solve, sympify
from extension_ost.inner_loop_helper import get_martingale_for_inner_loop


def try_get_bound(new_monomial, known_bounds):
    potential_martingales = list(get_martingale_for_inner_loop(list(set())))





# Some of the bounds are kind of duplicate. E.g. k>0 & y <= 0 => k*y <= 0
new_bound = try_get_bound("k**2", 
                          [("y*k",sympify("E(y*k) <= 0")), 
                           ("k",sympify("E(k) > 0")),
                           ("y",sympify("E(y) <= 0"))])
