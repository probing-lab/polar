from sympy import symbols, summation, sympify
from utils import without_piecewise, get_unique_var


def solve_rec_by_summing(rec_coeff, init_value, inhom_part, n):
    hom_solution = (rec_coeff ** n) * init_value
    k = symbols(get_unique_var('i'), integer=True, positive=True)

    print(f"inhom_part = {inhom_part}")
    print(f"inhom_part_replaced = {inhom_part.xreplace({n: n - k})}")

    summand = ((rec_coeff ** k) * inhom_part.xreplace({n: n - k})).simplify()

    # summand = (((rec_coeff ** k).simplify()) * (inhom_part.xreplace({n: n - k})).simplify()).simplify()


    print(f"summand = {summand}")

    particular_solution = summation(summand, (k, 0, (n - 1)))

    print(f"particular solution = {particular_solution}")

    particular_solution = without_piecewise(particular_solution)

    print(f"particular solution = {particular_solution}")

    print(f"hs = {hom_solution}")
    return (hom_solution + particular_solution).simplify()

if __name__ == '__main__':
    # n = symbols("n", integer=True, positive=True)
    # ans = solve_rec_by_summing(rec_coeff=sympify(2),init_value=1,inhom_part=sympify(1) + sympify(2),n=n)
    # print(ans)

    k = symbols('_i5', integer=True, positive=True)
    _u2 = symbols("_u2")
    _u3 = symbols("_u3")
    n = symbols("n", integer=True, positive=True)
    summand = (2 ** k) * (_u3 + _u2*(1/2 + (-1/2)*(-1)**(-k + n)))
    # summand2 = (2*u3 + u2*(1 - (-1)**(-k + n))) * (2 ** (-1 + k))


    print(f"summand = {summand}")
    # print(f"summand2 = {summand2}")

    ans = summation(summand, (k, 0, n - 1))
    # ans2 = summation(summand2, (k, 0, n - 1))
    print(f"ans = {ans}")
    # print(f"ans2 = {ans2}")