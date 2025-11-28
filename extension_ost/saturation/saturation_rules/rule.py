
from dataclasses import dataclass
from enum import Enum
from itertools import combinations, product
from typing import List, Literal, Tuple

from sympy import Add, Expr, Mul, sqrt

from extension_ost.saturation.saturation_rules.bound import Bound
from extension_ost.saturation.saturation_rules.initial_value_provider import InitialValueProvider
from extension_ost.saturation.saturation_rules.value_node import ValueNode

class RuleType(Enum):
    LB=0
    UB=1

class BoundRef(Enum):
    LB=0
    UB=1
    Const=2
    Sqrt=3
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.__str__()
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
                 inequalities: List[List[List[Tuple[Literal[0,1],int]]]]=[],
                 name:str=None): # positivity_constraints
        self.result = result
        self.result_type = result_type
        self.lbs = lbs
        self.ubs = ubs
        self.res_intercept = res_intercept
        self.inequalities = inequalities
        self.res_expr = res_expr
        self.name = name

    def _get_value(self, lbs, ubs, access: Tuple[Literal[0,1], int|Expr]):
        (c, a) = access
        if c == BoundRef.Const:
            return a
        if c == BoundRef.Sqrt:
            return sqrt(self._get_value(lbs, ubs, a))
        return (ubs if c == BoundRef.UB else lbs)[a].value
    
    def _get_expr(self, lbs, ubs, access: List[List[Tuple[BoundRef, int|Expr]]]):
        return Add(*[Mul(*[self._get_value(lbs, ubs, i) for i in mul_term]) for mul_term in access])

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
                ancestor_rules = set().union(*[lb.used_rules for lb in lbs]).union(*[ub.used_rules for ub in ubs])
                if self in ancestor_rules:
                    # cyclic dependency
                    return False
                # check the sign constraints of the bounds
                if any((not (self.result.initial_value_provider.is_nonnegative(self._get_expr(lbs, ubs, access)))) for access in self.inequalities):
                    continue

                new_candidate = Bound(self.res_intercept+self._get_expr(lbs, ubs, self.res_expr), ancestor_rules.union([self]))

                if self.result_type==RuleType.LB:
                    if self.result.add_lb(new_candidate):
                        was_updated = True
                        print(f"New derivation: {self.result.name} >= {new_candidate.value}")
                        print(f"\t\tusing: {self}")
                elif self.result_type==RuleType.UB:
                    if self.result.add_ub(new_candidate):
                        was_updated = True
                        print(f"New derivation: {self.result.name} <= {new_candidate.value}")
                        print(f"\t\tusing: {self}")

        return was_updated

    def __str__(self):
        premise = "/\\".join([str(ub.name)+f"<= a{i}" for i,ub in enumerate(self.ubs)]+
                             [str(lb.name)+f">= b{i}" for i,lb in enumerate(self.lbs)])
        op = "<=" if self.result_type==RuleType.UB else ">="
        concl = str(self.res_intercept)+"+"+str(self.res_expr)
        
        return premise+"==>"+str(self.result.name)+op+concl
