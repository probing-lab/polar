
from dataclasses import dataclass
from enum import Enum
from itertools import combinations, product
from typing import List

from sympy import Add, Expr

from extension_ost.saturation.saturation_rules.value_node import ValueNode

class RuleType(Enum):
    LB=0
    UB=1

class Rule:
    result: ValueNode
    result_type: RuleType

    lbs: List[ValueNode]
    ubs: List[ValueNode]

    res_lb_coeffs: List[Expr]
    res_ub_coeffs: List[Expr]

    def __init__(self, 
                 result: ValueNode,
                 result_type: RuleType,
                 lbs: List[ValueNode],
                 ubs: List[ValueNode],
                 res_lb_coeffs: List[Expr],
                 res_ub_coeffs: List[Expr]):
        self.result = result
        self.result_type = result_type
        self.lbs = lbs
        self.ubs = ubs
        self.res_lb_coeffs = res_lb_coeffs
        self.res_ub_coeffs = res_ub_coeffs
        assert len(lbs) == len(res_lb_coeffs)
        assert len(ubs) == len(res_ub_coeffs)

    def fire(self) -> bool:
        """_summary_

        Returns:
            bool: indicator whether a new bound was generated 
        """
        # TODO: this reevaluates everything. Some computation could be stored
        lbss = {tuple(x) for x in product(*[lb.lbs for lb in self.lbs])}
        ubss = {tuple(x) for x in product(*[lb.lbs for lb in self.lbs])}

        was_updated = False
        for lbs in lbss:
            for ubs in ubss:
                new_candidate = Add(*[a*b for a,b in zip(self.res_lb_coeffs, lbs)])+Add(*[a*b for a,b in zip(self.res_ub_coeffs, ubs)])
                if self.result_type==RuleType.LB:
                    if self.result.add_lb(new_candidate):
                        was_updated = True
                elif self.result_type==RuleType.UB:
                    if self.result.add_ub(new_candidate):
                        was_updated = True
        
        return was_updated
