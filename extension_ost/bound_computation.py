from copy import deepcopy
from typing import Dict, List, Set, Tuple
from sympy import Expr, Symbol, nan, solve, sympify
from itertools import chain, combinations

from extension_ost.bound_store import BoundStore
from extension_ost.expectation_map import ExpectationMapBuilder
from extension_ost.helpers import Expexted
from recurrences.rec_builder import RecBuilder


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
                   initial_constants: List[Tuple[Symbol, Expr, Expr]],
                   initial_lower_bounds: Dict[Expr, Expr],
                   initial_upper_bounds: Dict[Expr, Expr]):

    bound_store = BoundStore()
    for key, value in initial_upper_bounds.items():
        bound_store.add_upper_bound(key, value)
    for key, value in initial_lower_bounds.items():
        bound_store.add_lower_bound(key, value)
    for initial, lb, ub in initial_constants:
        bound_store.add_initial(initial, lb, ub)
    initial_value_dict = {var: sympify(recurrence_builder.get_initial_value(var)) for var in random_vars.union(deterministic_vars)}
    # Expexted is just a helper, with the main purpose of distributing and simplifying in accordance with Expected value of a RV
    initial_constants_sub = {Symbol(f"{sym}", real=True):sym for sym,_,_ in initial_constants}

    monoms_all = list(set(_get_monoms(random_vars.union(deterministic_vars), max_degree)))

    recurrences_all = {monom: recurrence_builder.get_recurrence(monom) for monom in monoms_all}
    # filter out the recurrences which are not iteration dependent - they destroy the procedure. TODO: Maybe adapt is_iteration_dependence of program for that
    recurrences = {k:v for k,v in recurrences_all.items() if k.free_symbols.issubset(v.free_symbols)}

    monoms = list(recurrences.keys())
    monoms.sort(key=lambda x: str(x))
    monom_subs = {f"E({monom})":monom for monom in monoms}
    monom_expexted_sub = {f"E({monom})": Expexted(monom) for monom in monoms}


    unprocessed:List[Expr] =deepcopy(monoms)
    exp_map_builder = ExpectationMapBuilder(recurrences, deterministic_vars, monom_subs)


    while len(unprocessed) > 0:
        goal_monom = next(iter(unprocessed))
        print("GOAL MONOM: ", goal_monom)
        unprocessed.remove(goal_monom)

        # There are potentially multiple martingales - maybe some of them lead to a bound, others dont
        martingales = set(exp_map_builder.get_expectation_maps(goal_monom))
        pass
        martingales.add(goal_monom)
        martingales.add(Expexted(goal_monom))

        for martingale_map in martingales:
            if martingale_map == goal_monom:
                solved_for_goal = martingale_map
                martingale_expexted = solved_for_goal
            elif martingale_map == Expexted(goal_monom):
                solved_for_goal = martingale_map
                martingale_expexted = solved_for_goal
            else:
                martingale_initial_value = martingale_map.subs(monom_subs).subs(initial_value_dict).simplify()

                martingale = martingale_map - martingale_initial_value
                # print("Martingale: ", martingale)
                martingale_expexted = martingale.subs(monom_expexted_sub).simplify()

                solved_for_goal = solve(martingale_expexted, Expexted(goal_monom))
                assert len(solved_for_goal) == 1, "Unsure if this asserting is actually true - hence added for finding out"
                solved_for_goal = solved_for_goal[0].subs(initial_constants_sub)

            upper_bounds = set(bound_store._get_upper_bounds_for_expression(solved_for_goal))
            pass
            for upper_bound in upper_bounds:
                upper_bound = upper_bound.simplify()
                if bound_store.is_new_upper_bound(Expexted(goal_monom), upper_bound):
                    bound_store.add_upper_bound(Expexted(goal_monom), upper_bound)
                    unprocessed = deepcopy(monoms)
                    print("\t",Expexted(goal_monom), "<=", upper_bound)
                    print("\t\t using:", martingale_expexted)
                else:
                    # print(Expexted(goal_monom), "<=", upper_bound)
                    pass

            lower_bounds = set(bound_store._get_lower_bounds_for_expression(solved_for_goal))
            pass
            for lower_bound in lower_bounds:
                lower_bound = lower_bound.simplify()
                if bound_store.is_new_lower_bound(Expexted(goal_monom), lower_bound):
                    bound_store.add_lower_bound(Expexted(goal_monom), lower_bound)
                    unprocessed = deepcopy(monoms)
                    print("\t",Expexted(goal_monom), ">=", lower_bound)
                    print("\t\t using:", martingale_expexted)
                else:
                    # print(Expexted(goal_monom), ">=", lower_bound)
                    pass

        if unprocessed == monoms:
            bound_store._pretty_print()
    bound_store._pretty_print()