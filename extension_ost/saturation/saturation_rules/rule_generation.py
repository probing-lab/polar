# this can be seen as a grounding instance
# of the general rule X <= a ==> E(X)<=a
from typing import Dict, Set

from sympy import S, Add, Expr, Mul, solve

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
                  [],
                  S.Zero)
        lb_dependencies[nodes[monom]].add(r1)
        yield r1
        r2 = Rule(nodes[Expexted(monom)],
                  RuleType.UB,
                  [],
                  [nodes[monom]],
                  [],
                  [1],
                  S.Zero)
        ub_dependencies[nodes[monom]].add(r2)
        yield r2


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
        UB_ub_coeffs = []
        UB_lb_values = []
        UB_lb_coeffs = []

        # For the rule that derives E(X) >= ...        
        LB_ub_values = []
        LB_ub_coeffs = []
        LB_lb_values = []
        LB_lb_coeffs = []

        ub_rule = Rule(nodes[monom_subs[str(exp_symbol)]], 
                       RuleType.UB,
                       UB_lb_values,
                       UB_ub_values,
                       UB_lb_coeffs,
                       UB_ub_coeffs,
                       S.Zero)

        lb_rule = Rule(nodes[monom_subs[str(exp_symbol)]], 
                       RuleType.LB,
                       LB_lb_values,
                       LB_ub_values,
                       LB_lb_coeffs,
                       LB_ub_coeffs,
                       S.Zero)

        for add_part in add_parts:
            terms = Mul.make_args(add_part)
            coeff = Mul(*[t for t in terms if t.is_number])
            exp_term = Mul(*[t for t in terms if not t.is_number])
            if not exp_term.has(Expexted):
                ub_rule.res_intercept += coeff*exp_term
            elif coeff.is_nonnegative:
                UB_ub_coeffs.append(coeff)
                UB_ub_values.append(nodes[exp_term])
                ub_dependencies[nodes[exp_term]].add(ub_rule)

                LB_lb_coeffs.append(coeff)
                LB_lb_values.append(nodes[exp_term])
                ub_dependencies[nodes[exp_term]].add(lb_rule)
            elif coeff.is_negative:
                UB_lb_coeffs.append(coeff)
                UB_lb_values.append(nodes[exp_term])
                ub_dependencies[nodes[exp_term]].add(lb_rule)

                LB_ub_coeffs.append(coeff)
                LB_ub_values.append(nodes[exp_term])
                ub_dependencies[nodes[exp_term]].add(ub_rule)
            else:
                raise ValueError("Coefficient must be number, hence sign must be known")
        yield ub_rule
        yield lb_rule