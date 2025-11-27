
from dataclasses import dataclass
from enum import Enum
from itertools import combinations, product
from typing import List, Literal, Tuple

from sympy import Add, Expr, Mul

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
                 res_expr: List[List[Tuple[Literal[0,1],int]]],
                 res_intercept: Expr,
                 positive_bounds: List[Tuple[Literal[0,1],int]]=[], # the indices of the upper bounds, which must be nonnegative
                 negative_bounds: List[Tuple[Literal[0,1],int]]=[], # indices of nonpositive ubs
                 inequalities: List[Tuple[Literal[0,1],int]]=[]): # given (c,a), (d,b), check whether a <= d, and 
        self.result = result
        self.result_type = result_type
        self.lbs = lbs
        self.ubs = ubs
        self.res_intercept = res_intercept
        self.inequalities = inequalities
        self.res_expr = res_expr
        self.positive_bounds = positive_bounds
        self.negative_bounds = negative_bounds

    def _get_value(self, lbs, ubs, access: Tuple[Literal[0,1], int|Expr]):
        (c, a) = access
        if c == 2:
            return a
        return (ubs if c == 1 else lbs)[a]

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
                if any((not self.result.initial_value_provider.is_nonnegative(self._get_value(lbs, ubs, i))) for i in self.positive_bounds):
                    continue
                if any((not self.result.initial_value_provider.is_nonnegative(-self._get_value(lbs, ubs, i))) for i in self.negative_bounds):
                    continue
                
                if any((not (self.result.initial_value_provider.is_nonnegative(
                     self._get_value(lbs, ubs, i1)-self._get_value(lbs, ubs, i2))) for i1, i2 in self.inequalities)):
                    continue

                new_candidate = self.res_intercept+Add(*[Mul(*[self._get_value(lbs, ubs, i) for i in mul_term]) for mul_term in self.res_expr])

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
        concl = str(self.res_intercept)+"+"+str(self.res_expr)
        
        return premise+"==>"+str(self.result.name)+op+concl
