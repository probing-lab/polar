from typing import Dict, List, Tuple
from sympy import (
    Expr,
    Monomial,
    Poly,
    Symbol,
    degree,
    expand,
    limit,
    oo,
    prod,
    simplify,
    summation,
    symbols,
    sympify,
)
from sympy import Poly as sympy_Poly
from program.assignment.dist_assignment import DistAssignment
from termination.martingales.asymptotics import dominated, dominating
from termination.util.constants import ITER_VAR
from termination.util.helpers import (
    amber_limit,
    inhom,
    recurrence_constant,
    unique_positive_symbol,
)
from termination.util.poly_utils import get_possible_signs


def compute_bounds_of_expr(
    poly: Poly,
    branches: Dict[Symbol, List[Tuple[Expr, Expr]]],
    dist_assignments: Dict[Symbol, DistAssignment],
    closed_forms: Dict[Symbol, Expr],
    initial_values: Dict[Symbol, Expr],
):
    """
    Compute the bounds of a poly given its possible update-branches
    """
    if poly.is_number:
        return poly, poly
    expression = sympify(poly)
    if poly.free_symbols:
        poly = Poly(poly.subs({s: Symbol(str(s)) for s in poly.free_symbols}))
    lb = expression
    ub = expression
    monoms = [prod(x**k for x, k in zip(poly.gens, mon)) for mon in poly.monoms()]
    print(expression.__class__)

    for monom in monoms:
        print(monom.__class__)

        rvs, m = _separate_rvs_from_monom(monom, dist_assignments)
        l_bound, u_bound = compute_bounds_of_monom(
            m, branches, dist_assignments, closed_forms, initial_values
        )
        if rvs:
            monom_bounds = _multiply_rvs_for_monom_bounds(
                rvs, l_bound, u_bound, monom, dist_assignments
            )
        else:
            monom_bounds = l_bound, u_bound
        lb, ub = _replace_monom_in_expr_bounds(monom, monom_bounds, expression, lb, ub)

    upper_candidates = [ub]
    lower_candidates = [lb]

    ub = dominating(upper_candidates, ITER_VAR)
    lb = dominated(lower_candidates, ITER_VAR)
    return lb, ub


def _separate_rvs_from_monom(monom, dist_assignments: Dict[Symbol, DistAssignment]):
    rvs = []
    rem = monom
    for symbol in monom.free_symbols:
        deg = degree(monom, gen=symbol)
        if symbol in dist_assignments:
            rvs.append((symbol, deg))
            rem = rem.subs({symbol**deg: 1})
    return rvs, rem


def _replace_monom_in_expr_bounds(monom, monom_bounds, expression, lb, ub):
    coeff = expression.as_expr().coeff(monom)
    coeff = amber_limit(coeff)

    if coeff.is_positive:
        upper = monom_bounds[1]
        lower = monom_bounds[0]
    else:
        upper = monom_bounds[1]
        lower = monom_bounds[0]

    return lb.subs({monom: lower}), ub.subs({monom: upper})


def _multiply_rvs_for_monom_bounds(
    rvs, l_bound, u_bound, monomial, dist_assignments: Dict[Symbol, DistAssignment]
):
    for rv, power in rvs:
        candidates = []

        for cand in dist_assignments[rv].get_support():  # TODO: Missing power?
            if isinstance(cand, tuple):
                candidates.append(cand[0] * l_bound)
                candidates.append(cand[0] * u_bound)
                candidates.append(cand[1] * l_bound)
                candidates.append(cand[1] * u_bound)
            else:
                candidates.append(cand * l_bound)
                candidates.append(cand * u_bound)

        u_bound = dominating(candidates, ITER_VAR)
        l_bound = dominated(candidates, ITER_VAR)

    return l_bound, u_bound


def _monom_is_deterministic(
    monom: Monomial,
    branches: Dict[Symbol, List[Tuple[Expr, Expr]]],
    closed_forms: Dict[Symbol, Expr],
):
    if not monom.free_symbols:
        return True  # constant
    return (monom.free_symbols & closed_forms.keys()) == monom.free_symbols


def compute_bounds_of_monom(
    monom: Monomial,
    branches: Dict[Symbol, List[Tuple[Expr, Expr]]],
    dist_assignments: Dict[Symbol, DistAssignment],
    closed_forms: Dict[Symbol, Expr],
    initial_values: Dict[Symbol, Expr],
):
    if _monom_is_deterministic(monom, branches, dist_assignments):
        # Substitute with closed form
        bound = simplify(monom.subs(closed_forms))
        return bound, bound

    # TODO: Shortcut with negative power

    # Solve recurrence (this basically resembles __compute_bounds_of_monom_recurrence,
    # which also basically is Algorithm 1 from
    # "Automated TerminationAnalysis of Polynomial Probabilistic Programs, Mossbrugger et. al.")

    assert monom in branches
    # TODO: Ask marcel why "b.lower.xreplace({n: n - 1})" in amber
    inhom_bounds_upper = [
        compute_bounds_of_expr(
            b, branches, dist_assignments, closed_forms, initial_values
        )[1]
        for b in inhom(branches[monom], monom)
    ]
    inhom_bounds_lower = [
        compute_bounds_of_expr(
            b, branches, dist_assignments, closed_forms, initial_values
        )[0]
        for b in inhom(branches[monom], monom)
    ]

    max_upper = dominating(inhom_bounds_upper, ITER_VAR)
    min_lower = dominated(inhom_bounds_lower, ITER_VAR)

    min_rec = min(recurrence_constant(branches[monom], monom))
    max_rec = max(recurrence_constant(branches[monom], monom))

    maybe_pos, maybe_neg = get_possible_signs(
        *branches, *inhom_bounds_lower, *inhom_bounds_upper, monom.subs(initial_values)
    )

    I = set()
    if maybe_pos:
        I.add(unique_positive_symbol())
    if maybe_neg:
        I.add(-unique_positive_symbol())
    if len(I) == 0:
        I.add(sympify(0))

    coeff_upper = {max_rec}
    if maybe_neg:
        coeff_upper.add(min_rec)

    coeff_lower = {min_rec}
    if maybe_pos:
        coeff_upper.add(max_rec)

    upper_candidates = _compute_bound_candidates(coeff_upper, {max_upper}, I)
    lower_candidates = _compute_bound_candidates(coeff_lower, {min_lower}, I)

    max_upper_candidate = dominating(upper_candidates, ITER_VAR)
    min_lower_candidate = dominated(lower_candidates, ITER_VAR)

    if not maybe_pos:
        max_upper_candidate = dominated([max_upper_candidate, sympify(0)], ITER_VAR)

    if not maybe_neg:
        min_lower_candidate = dominating([min_lower_candidate, sympify(0)], ITER_VAR)

    return max_upper_candidate, min_lower_candidate


def _compute_bound_candidates(
    coefficients: List[Expr], inhom_parts: List[Expr], starting_values: List[Expr]
) -> List[Expr]:
    """
    Computes functions which could potentially be bounds
    """
    candidates = []

    for c in coefficients:
        for part in inhom_parts:
            c0 = symbols("c0")
            solution = _compute_bound_candidate(c, part, c0)
            for v in starting_values:
                solution = solution.xreplace({c0: v})
                # If a candidate contains signum functions, we have to split the candidate into more candidates
                new_candidates = [solution]  # TODO: removed split_on_signums
                candidates += new_candidates

    return candidates


def _compute_bound_candidate(
    c: List[Expr], inhom_part: Expr, starting_value: Expr
) -> Expr:
    """
    Computes a single function which is potentially a bound by solving a recurrence relation
    """
    ITER_VAR
    if c.is_zero:
        return expand(inhom_part.xreplace({ITER_VAR: ITER_VAR - 1}))

    hom_solution = (c**ITER_VAR) * starting_value
    k = symbols("_k", integer=True, positive=True)
    summand = simplify((c**k) * inhom_part.xreplace({ITER_VAR: (ITER_VAR - 1) - k}))
    particular_solution = summation(summand, (k, 0, (ITER_VAR - 1)))
    solution = simplify(hom_solution + particular_solution)
    return solution
