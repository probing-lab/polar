# this can be seen as a grounding instance
# of the general rule X <= a ==> E(X)<=a
from typing import Dict, Set

from sympy import Expr

from extension_ost.helpers import Expexted
from extension_ost.saturation.saturation_rules.rule import Rule, RuleType

# This basically is grounding of the rule
# X <= a ==> E(X) <= a  (and similar for >=)


def generate_hard_bound_rules(monoms, nodes,
                              lb_dependencies: Dict[Expr, Set[Rule]],
                              ub_dependencies: Dict[Expr, Set[Rule]]):
    for monom in monoms:

        r1 = Rule(nodes[Expexted(monom)],
                  RuleType.LB,
                  [nodes[monom]],
                  [],
                  [1],
                  [])
        lb_dependencies[nodes[monom]].add(r1)
        yield r1
        r2 = Rule(nodes[Expexted(monom)],
                  RuleType.UB,
                  [],
                  [nodes[monom]],
                  [],
                  [1])
        ub_dependencies[nodes[monom]].add(r2)
        yield r2


def generate_martingale_based_rule(expression_map,
                                   nodes,
                                   lb_dependencies,
                                   ub_dependencies):
    pass
