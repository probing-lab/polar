from typing import Dict, List, Set

from sympy import Expr
from extension_ost.saturation.saturation_rules.rule import Rule, RuleType
from extension_ost.saturation.saturation_rules.value_node import ValueNode


def saturate(nodes: List[ValueNode], 
             rules: List[Rule],
             lb_dependencies:Dict[Expr, Set[Rule]],
             ub_dependencies:Dict[Expr, Set[Rule]]):
    
    unprocessed: Set[Rule] = set(rules)
    while len(unprocessed) > 0:
        rule = unprocessed.pop()

        res = rule.fire()
        if res:
            old_l = len(unprocessed)
            unprocessed = unprocessed.union(
                (lb_dependencies if rule.result_type == RuleType.LB else ub_dependencies)[rule.result]
            )
            new_l = len(unprocessed)
            print(f"- Unprocessed {old_l} -> {new_l}")

    return nodes
