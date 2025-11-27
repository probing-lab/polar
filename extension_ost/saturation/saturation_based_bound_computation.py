from collections import defaultdict
from typing import List, Set, Tuple, Dict
from sympy import Symbol, Expr

from extension_ost.expectation_map import ExpectationMapBuilder
from extension_ost.helpers import Expexted
from extension_ost.saturation.saturation_algorithm import saturate
from extension_ost.saturation.saturation_rules.rule_generation import generate_hard_bound_rules
from extension_ost.saturation.saturation_rules.initial_value_provider import InitialValueProvider
from extension_ost.saturation.saturation_rules.rule import Rule, RuleType
from extension_ost.saturation.saturation_rules.value_node import ValueNode
from extension_ost.square_extraction import reformulate_maps_with_squares
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

def compute_bounds_saturation(random_vars: Set[Symbol],
                   deterministic_vars: Set[Symbol],
                   max_degree: int,
                   recurrence_builder: RecBuilder,
                   initial_constants: List[Tuple[Symbol, Expr, Expr]],
                   initial_lower_bounds: Dict[Expr, Expr],
                   initial_upper_bounds: Dict[Expr, Expr]):

    monoms_all = list(set(_get_monoms(random_vars.union(deterministic_vars), max_degree)))
    recurrences_all = {monom: recurrence_builder.get_recurrence(monom) for monom in monoms_all}
    # filter out the recurrences which are not iteration dependent - they destroy the procedure. TODO: Maybe adapt is_iteration_dependence of program for that
    recurrences = {k:v for k,v in recurrences_all.items() if k.free_symbols.issubset(v.free_symbols)}

    monoms = list(recurrences.keys())
    monoms.sort(key=lambda x: str(x))
    monom_subs = {f"E({monom})":monom for monom in monoms}
    monom_expexted_sub = {f"E({monom})": Expexted(monom) for monom in monoms}

    exp_map_builder = ExpectationMapBuilder(recurrences, deterministic_vars)

    exp_maps = []
    for monom in monoms:
        exp_maps += exp_map_builder.get_expectation_maps(monom)
    exp_maps_filtered = exp_map_builder.filter_unique_primitives(exp_maps)
    
    extracted_square_maps = reformulate_maps_with_squares(exp_maps_filtered, monom_expexted_sub)
    extracted_square_maps_filtered = exp_map_builder.filter_unique_primitives(extracted_square_maps)    
    

    initial_value_provider = InitialValueProvider()
    for symbol, lb, ub in initial_constants:
        initial_value_provider.add_initial(symbol, lb, ub)

    # Creation of Nodes and Rules begins

    bound_exprs = monoms+[Expexted(monom) for monom in monoms]

    nodes = {bound_expr: ValueNode(initial_value_provider, bound_expr) for bound_expr in bound_exprs}

    # Fill with initial knowledge (basically negated loopgard and positivity of k)
    for k,v in initial_lower_bounds.items():
        nodes[k].add_lb(v)
    for k,v in initial_upper_bounds.items():
        nodes[k].add_ub(v)

    # if a lower (or upper) bound is added to the key, all its rules (the value)
    # need to be added to unprocessed
    lb_dependencies:Dict[Expr, Set[Rule]] = defaultdict(set)
    ub_dependencies:Dict[Expr, Set[Rule]] = defaultdict(set)

    rules = []
    rules += list(generate_hard_bound_rules(monoms, nodes, lb_dependencies, ub_dependencies))

    
    return saturate(nodes, rules, lb_dependencies, ub_dependencies)


