
from dataclasses import dataclass
from enum import Enum
from itertools import combinations, product
from typing import List, Literal, Tuple

from sympy import Add, Expr

from extension_ost.saturation.saturation_rules.initial_value_provider import InitialValueProvider
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
                 res_ub_coeffs: List[Expr],
                 res_intercept: Expr,
                 positive_ubs: List[int]=[], # the indices of the upper bounds, which must be nonnegative
                 negative_ubs: List[int]=[], # indices of nonpositive ubs
                 positive_lbs: List[int]=[], # ... lbs
                 negative_lbs: List[int]=[],# ... lbs
                 inequalities: List[Tuple[Literal[0,1],int]]=[]): # given (c,a), (d,b), check whether a <= d, and 
        self.result = result
        self.result_type = result_type
        self.lbs = lbs
        self.ubs = ubs
        self.res_lb_coeffs = res_lb_coeffs
        self.res_ub_coeffs = res_ub_coeffs
        self.res_intercept = res_intercept
        assert len(lbs) == len(res_lb_coeffs)
        assert len(ubs) == len(res_ub_coeffs)
        self.positive_ubs = positive_ubs
        self.negative_ubs = negative_ubs
        self.positive_lbs = positive_lbs
        self.negative_lbs = negative_lbs
        self.inequalities = inequalities

    def fire(self) -> bool:
        """_summary_

        Returns:
            bool: indicator whether a new bound was generated 
        """
        # TODO: this reevaluates everything. Some computation could be stored
        lbss = list(product(*[lb.lbs for lb in self.lbs]))
        ubss = list(product(*[ub.ubs for ub in self.ubs]))

        was_updated = False
        for lbs in lbss:
            for ubs in ubss:
                # check the sign constraints of the bounds
                if any(not self.result.initial_value_provider.is_nonnegative(self.ubs[i]) for i in self.positive_ubs):
                    continue
                if any(not self.result.initial_value_provider.is_nonnegative(-self.ubs[i]) for i in self.negative_ubs):
                    continue
                if any(not self.result.initial_value_provider.is_nonnegative(self.lbs[i]) for i in self.positive_lbs):
                    continue
                if any(not self.result.initial_value_provider.is_nonnegative(-self.lbs[i]) for i in self.negative_lbs):
                    continue
                
                if any(not (self.result.initial_value_provider.is_nonnegative(
                     (ubs if c == 1 else lbs)[a]-(ubs if d == 1 else lbs)[b]) for (c,a),(d,b) in self.inequalities)):
                    continue


                new_candidate = Add(*[a*b for a,b in zip(self.res_lb_coeffs, lbs)])+Add(*[a*b for a,b in zip(self.res_ub_coeffs, ubs)])+self.res_intercept
                if self.result_type==RuleType.LB:
                    if self.result.add_lb(new_candidate):
                        was_updated = True
                elif self.result_type==RuleType.UB:
                    if self.result.add_ub(new_candidate):
                        was_updated = True
        
        return was_updated

    def __str__(self):
        premise = "/\\".join([str(ub.name)+f"<= a{i}" for i,ub in enumerate(self.ubs)]+
                             [str(lb.name)+f">= b{i}" for i,lb in enumerate(self.lbs)])
        op = "<=" if self.result_type==RuleType.UB else ">="
        concl = "+".join([str(self.res_intercept)]+[f"a{i}*{coeff}" for i, coeff in enumerate(self.res_ub_coeffs)]+
                         [f"b{i}*{coeff}" for i, coeff in enumerate(self.res_lb_coeffs)])
        
        return premise+"==>"+str(self.result.name)+op+concl