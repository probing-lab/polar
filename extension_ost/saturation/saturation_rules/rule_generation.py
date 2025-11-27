# this can be seen as a grounding instance
# of the general rule X <= a ==> E(X)<=a
from itertools import product
from typing import Dict, Set

from sympy import S, Add, Expr, Mul, simplify, solve

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
                  [[(0, 0)]],
                  S.Zero)
        lb_dependencies[nodes[monom]].add(r1)
        yield r1
        r2 = Rule(nodes[Expexted(monom)],
                  RuleType.UB,
                  [],
                  [nodes[monom]],
                  [[(1,0)]],
                  S.Zero)
        ub_dependencies[nodes[monom]].add(r2)
        yield r2

def generate_var_multiplication_ub_rules(monoms, nodes,
                                      lb_dependencies,
                                      ub_dependencies):
    # we are in the general setting:
    # a <= X <= b
    # c <= Y <= d
    for X, Y in product(monoms, monoms):
        if simplify(X*Y) not in monoms and simplify(Y*X) not in monoms:
            continue # to high degree
        res_monom = simplify(X*Y) if simplify(X*Y) in monoms else simplify(Y*X)

        # a >= 0, b>= 0, c>= 0 => XY<= bd
        rule1 = Rule(res_monom, 
                     RuleType.UB,
                     [nodes[X]],
                     [nodes[X], nodes[Y]],
                     [])

def generate_rv_multiplication_rules(monoms, nodes,
                                    lb_dependencies,
                                    ub_dependencies):
    """Generates rules for deriving bounds

    Args:
        monoms (_type_): _description_
        nodes (_type_): _description_
        lb_dependencies (_type_): _description_
        ub_dependencies (_type_): _description_
    """
    pass

def generate_martingale_based_rule(expression_map: Expr,
                                   nodes: Dict[Expr, Expr],
                                   lb_dependencies: Dict[Expr, Set[Rule]],
                                   ub_dependencies: Dict[Expr, Set[Rule]],
                                   monom_subs: Dict[Expr, Expr]):
    """For every expression map b1\*E(X1)+...+bk\*E(Xk)+b0=0, create a set of rule:
    E(X2) <= a2 /\\ ... /\\ E(Xk)<=ak ==> E(X1) >= -b0 + a2\*b2+...+ak\*bk

    And the same for the upper bounds. Also switch the sign of the inequality based on the sign of bi

    Args:
        expression_map (Expr): the expression map for which to generate the rules
        nodes (Dict[Expr, Expr]): nodes storing bounds of monomials
        lb_dependencies (Dict[Expr, Rule]): dictionary to store lb dependencies
        ub_dependencies (Dict[Expr, Rule]): dictionary to store ub dependencies
        monom_subs (Dict[Expr, Expr]): mapping of E(X) to Expexted(X)
    """
    expectation_symbols = {sym for sym in expression_map.free_symbols if str(sym).startswith("E(")}
    for exp_symbol in expectation_symbols:
        solved_expr = solve(expression_map, exp_symbol)[0].subs(monom_subs)

        add_parts = Add.make_args(solved_expr)

        # For the rule that derives E(X) <= ...        
        UB_ub_values = []
        UB_lb_values = []
        UB_coeffs = []
        UB_i = 0

        # For the rule that derives E(X) >= ...        
        LB_ub_values = []
        LB_lb_values = []
        LB_coeffs = []
        LB_i = 0

        ub_rule = Rule(nodes[monom_subs[str(exp_symbol)]], 
                       RuleType.UB,
                       UB_lb_values,
                       UB_ub_values,
                       UB_coeffs,
                       S.Zero)

        lb_rule = Rule(nodes[monom_subs[str(exp_symbol)]], 
                       RuleType.LB,
                       LB_lb_values,
                       LB_ub_values,
                       LB_coeffs,
                       S.Zero)

        for add_part in add_parts:
            terms = Mul.make_args(add_part)
            coeff = Mul(*[t for t in terms if t.is_number])
            exp_term = Mul(*[t for t in terms if not t.is_number])
            if not exp_term.has(Expexted):
                ub_rule.res_intercept += coeff*exp_term
            elif coeff.is_nonnegative:
                UB_coeffs.append([(1,len(UB_ub_values)), (2, coeff)])
                UB_ub_values.append(nodes[exp_term])
                ub_dependencies[nodes[exp_term]].add(ub_rule)

                LB_coeffs.append([(0,len(LB_lb_values)), (2, coeff)])
                LB_lb_values.append(nodes[exp_term])
                lb_dependencies[nodes[exp_term]].add(lb_rule)

                UB_i+=1
                LB_i+=1
            elif coeff.is_negative:
                UB_coeffs.append([(0,len(UB_lb_values)), (2, coeff)])
                UB_lb_values.append(nodes[exp_term])
                ub_dependencies[nodes[exp_term]].add(lb_rule)

                LB_coeffs.append([(1,len(LB_ub_values)), (2, coeff)])
                LB_ub_values.append(nodes[exp_term])
                lb_dependencies[nodes[exp_term]].add(ub_rule)

                UB_i+=1
                LB_i+=1
            else:
                raise ValueError("Coefficient must be number, hence sign must be known")
        yield ub_rule
        yield lb_rule