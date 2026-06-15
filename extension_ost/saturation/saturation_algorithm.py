from typing import Dict, List, Set

from sympy import Expr
from extension_ost.saturation.rule_queue import RuleQueue
from extension_ost.saturation.saturation_rules.rule import Rule, RuleType
from extension_ost.saturation.saturation_rules.value_node import ValueNode


def saturate(nodes: List[ValueNode], 
             rules: List[Rule],
             lb_dependencies:Dict[Expr, Set[Rule]],
             ub_dependencies:Dict[Expr, Set[Rule]]):
    
    unprocessed: RuleQueue = RuleQueue(rules)
    while len(unprocessed.heap) > 0:
        rule = unprocessed.get_next()

        res = rule.fire()
        if res:
            old_l = len(unprocessed.heap)
            unprocessed.add_rules((lb_dependencies if rule.result_type == RuleType.LB else ub_dependencies)[rule.result])
            new_l = len(unprocessed.heap)
            print(f"- Unprocessed {old_l} -> {new_l}")

    return nodes
