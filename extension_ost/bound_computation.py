from copy import deepcopy
from typing import Dict, List, Set
from sympy import Expr, Symbol, solve, sympify
from symengine.lib.symengine_wrapper import sympify as se_sympify
from itertools import chain, combinations

from extension_ost.bound_store import BoundStore
from extension_ost.expectation_map import get_expectation_maps
from extension_ost.helpers import Expexted
from ost_quadr_time import powerset
from recurrences.rec_builder import RecBuilder

def _powerset(seq):
    """
    Returns all the subsets of this set. This is a generator.
    """
    if len(seq) <= 1:
        yield seq
        yield []
    else:
        for item in powerset(seq[1:]):
            yield [seq[0]]+item
            yield item

def _get_monoms(symbols: List[Symbol],
                max_degree):
    for symbol in symbols:
        if max_degree > 1:
            for monom_part in _get_monoms(symbols, max_degree-1):
                yield symbol*monom_part
                yield monom_part
        else:
            yield symbol

def compute_bounds(random_vars: Set[Symbol],
                   deterministic_vars: Set[Symbol],
                   max_degree: int,
                   recurrence_builder: RecBuilder,
                   initial_constants: List[Symbol],
                   initial_lower_bounds: Dict[Expr, Expr],
                   initial_upper_bounds: Dict[Expr, Expr]):

    monoms = list(set(_get_monoms(random_vars.union(deterministic_vars), max_degree)))

    unprocessed:List[Expr] =deepcopy(monoms)

    bound_store = BoundStore()
    bound_store.upper_bounds = initial_upper_bounds
    bound_store.lower_bounds = initial_lower_bounds
    bound_store.initials = set(initial_constants)
    initial_value_dict = {var: recurrence_builder.get_initial_value(var) for var in random_vars.union(deterministic_vars)}
    monom_subs = {f"E({monom})":monom for monom in monoms}
    # Expexted is just a helper, with the main purpose of distributing and simplifying in accordance with Expected value of a RV
    monom_expexted_sub = {f"E({monom})": Expexted(monom) for monom in monoms}

    while len(unprocessed) > 0:
        goal_monom = next(iter(unprocessed))
        unprocessed.remove(goal_monom)

        for options in _powerset(monoms):
            if goal_monom not in options or len(options) == 0:
                continue

            recurrences = {monom: recurrence_builder.get_recurrence(se_sympify(monom)) for monom in options} # TODO: Dirty fix with symengine. This needs a systematic change

            # There are potentially multiple martingales - maybe some of them lead to a bound, others dont
            martingales = get_expectation_maps(recurrences, goal_monom, deterministic_vars)

            for martingale_map in martingales:
                martingale_initial_value = martingale_map.subs(monom_subs).subs(initial_value_dict).simplify()

                martingale = martingale_map - martingale_initial_value
                martingale_expexted = martingale.subs(monom_expexted_sub).simplify()

                solved_for_goal = solve(martingale_expexted, Expexted(goal_monom))
                assert len(solved_for_goal) == 1, "Unsure if this asserting is actually true - hence added for finding out"
                solved_for_goal = solved_for_goal[0]

                upper_bound = bound_store._get_upper_bound_for_expression(solved_for_goal)
                lower_bound = bound_store._get_lower_bound_for_expression(solved_for_goal)

                print(goal_monom, upper_bound)
                print(goal_monom, lower_bound)
                pass


    pass