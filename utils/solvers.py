from sympy import symbols, summation
from utils import without_piecewise, get_unique_var


def solve_rec_by_summing(rec_coeff, init_value, inhom_part):
    for item in inhom_part.free_symbols:
        if str(item) == "n":
            n = item

    print(f"solving c[n] = {rec_coeff}c[n - 1] + {inhom_part}")

    hom_solution = (rec_coeff ** n) * init_value
    k = symbols(get_unique_var('k'), integer=True, positive=True)
    summand = ((rec_coeff ** k) * inhom_part.xreplace({n: n - k})).simplify()
    particular_solution = summation(summand, (k, 0, (n - 1)))
    particular_solution = without_piecewise(particular_solution)
    return (hom_solution + particular_solution).simplify()

if __name__ == '__main__':
    n = symbols("n", integer=True, positive=True)
    inhom_part = n
    ans = solve_rec_by_summing(
        rec_coeff=1,
        init_value=1,
        inhom_part=inhom_part
    )
    print(ans)