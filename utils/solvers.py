from sympy import symbols, summation
from utils import without_piecewise, get_unique_var


def solve_rec_by_summing(rec_coeff, init_value, inhom_part, n):
    hom_solution = (rec_coeff ** n) * init_value
    k = symbols(get_unique_var('k'), integer=True, positive=True)
    summand = ((rec_coeff ** k) * inhom_part.xreplace({n: n - k})).simplify()
    particular_solution = summation(summand, (k, 0, (n - 1)))
    particular_solution = without_piecewise(particular_solution)
    return (hom_solution + particular_solution).simplify()