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
                  [[(1, 0)]],
                  S.Zero)
        ub_dependencies[nodes[monom]].add(r2)
        yield r2

def generate_var_multiplication_ub_rules(monoms,
                                         nodes: Dict[Expr, Expr],
                                         lb_dependencies: Dict[Expr, Set[Rule]],
                                         ub_dependencies: Dict[Expr, Set[Rule]]):
    # we are in the general setting:
    # a <= X <= b
    # c <= Y <= d
    for X, Y in product(monoms, monoms):
        if simplify(X*Y) not in monoms and simplify(Y*X) not in monoms:
            continue  # to high degree
        res_monom = simplify(X*Y) if simplify(X*Y) in monoms else simplify(Y*X)

        # a >= 0, b>= 0, c>= 0 => XY<= bd
        rule1 = Rule(nodes[res_monom],
                     RuleType.UB,
                     [nodes[X]],
                     [nodes[X], nodes[Y]],
                     [[(1, 0), (1, 1)]],
                     S.Zero,
                     inequalities=[[[(0,0)]],
                                   [[(1,0)]],
                                   [[(1,1)]]])
        lb_dependencies[nodes[X]].add(rule1)
        ub_dependencies[nodes[X]].add(rule1)
        ub_dependencies[nodes[Y]].add(rule1)
        yield rule1

        # a >= 0, d <= 0 => XY <= ad
        rule2 = Rule(nodes[res_monom],
                     RuleType.UB,
                     [nodes[X]],
                     [nodes[Y]],
                     [[(0, 0), (1, 0)]],
                     S.Zero,
                     inequalities=[[[(0,0)]],
                                   [[(1,0),(2,-S.One)]]])
        lb_dependencies[nodes[X]].add(rule2)
        ub_dependencies[nodes[Y]].add(rule2)
        yield rule2

        # a <= 0, c <= 0, d <= 0
        rule3 = Rule(nodes[res_monom],
                     RuleType.UB,
                     [nodes[X], nodes[Y]],
                     [nodes[Y]],
                     [[(0,0),(0,1)]],
                     S.Zero,
                     inequalities=[[[(0,0),(2,-S.One)]],
                                   [[(0,1),(2,-S.One)]],
                                   [[(1,0),(2,-S.One)]]])
        lb_dependencies[nodes[X]].add(rule3)
        lb_dependencies[nodes[Y]].add(rule3)
        ub_dependencies[nodes[Y]].add(rule3)
        yield rule3

        # a <= 0, b >= 0, c <= 0, d >=0, ac >= bd => XY <= ac
        rule4 = Rule(nodes[res_monom],
                     RuleType.UB,
                     [nodes[X], nodes[Y]],
                     [nodes[X], nodes[Y]],
                     [[(0,0),(0,1)]],
                     S.Zero,
                     inequalities=[[[(0,0),(2,-S.One)]],
                                   [[(0,1),(2,-S.One)]],
                                   [[(1,0)]],
                                   [[(1,1)]],
                                   [[(0,0), (0,1)],[(1,0),(1,1),(2,-S.One)]]]) # check whether ac-bd is nonnegative
        lb_dependencies[nodes[X]].add(rule4)
        lb_dependencies[nodes[Y]].add(rule4)
        ub_dependencies[nodes[X]].add(rule4)
        ub_dependencies[nodes[Y]].add(rule4)
        yield rule4
        
        # a <= 0, b >= 0, c <= 0, d >=0, ac >= bd => XY <= bd
        rule5 = Rule(nodes[res_monom],
                     RuleType.UB,
                     [nodes[X], nodes[Y]],
                     [nodes[X], nodes[Y]],
                     [[(1,0),(1,1)]],
                     S.Zero,
                     inequalities=[[[(0,0),(2,-S.One)]],
                                   [[(0,1),(2,-S.One)]],
                                   [[(1,0)]],
                                   [[(1,1)]],
                                   [[(0,0), (0,1),(2,-S.One)],[(1,0),(1,1)]]]) # check whether bd-ac is nonnegative
        lb_dependencies[nodes[X]].add(rule5)
        lb_dependencies[nodes[Y]].add(rule5)
        ub_dependencies[nodes[X]].add(rule5)
        ub_dependencies[nodes[Y]].add(rule5)
        yield rule5

def generate_var_multiplication_lb_rules(monoms,
                                         nodes: Dict[Expr, Expr],
                                         lb_dependencies: Dict[Expr, Set[Rule]],
                                         ub_dependencies: Dict[Expr, Set[Rule]]):
    # we are in the general setting:
    # a <= X <= b
    # c <= Y <= d
    for X, Y in product(monoms, monoms):
        if simplify(X*Y) not in monoms and simplify(Y*X) not in monoms:
            continue  # to high degree
        res_monom = simplify(X*Y) if simplify(X*Y) in monoms else simplify(Y*X)

        # b<=0, d<=0 => bd <= XY
        rule1 = Rule(nodes[res_monom],
                     RuleType.LB,
                     [],
                     [nodes[X], nodes[Y]],
                     [[(1, 0), (1, 1)]],
                     S.Zero,
                     inequalities=[[[(1,0),(2,-S.One)]],
                                   [[(1,1),(2,-S.One)]]])
        ub_dependencies[nodes[X]].add(rule1)
        ub_dependencies[nodes[Y]].add(rule1)
        yield rule1

        # b>=0, c<=0, d<=0 ==> bc <= XY
        rule2 = Rule(nodes[res_monom],
                     RuleType.LB,
                     [nodes[Y]],
                     [nodes[X], nodes[Y]],
                     [[(0, 0), (1, 0)]],
                     S.Zero,
                     inequalities=[[[(0,0),(2,-S.One)]],
                                   [[(1,1),(2,-S.One)]],
                                   [[(1,0)]]])
        ub_dependencies[nodes[X]].add(rule2)
        ub_dependencies[nodes[Y]].add(rule2)
        lb_dependencies[nodes[Y]].add(rule2)
        yield rule2

        # a >= 0, b>=0, c <= 0 ==> bc <= XY
        rule3 = Rule(nodes[res_monom],
                     RuleType.LB,
                     [nodes[X], nodes[Y]],
                     [nodes[X]],
                     [[(0, 1), (1, 0)]],
                     S.Zero,
                     inequalities=[[[(0,1),(2,-S.One)]],
                                   [[(0,0)]],
                                   [[(1,0)]]])
        lb_dependencies[nodes[X]].add(rule3)
        lb_dependencies[nodes[Y]].add(rule3)
        ub_dependencies[nodes[X]].add(rule3)
        yield rule3

        # a >= 0, c >= 0 ==> ac <= XY
        rule4 = Rule(nodes[res_monom],
                     RuleType.LB,
                     [nodes[X], nodes[Y]],
                     [],
                     [[(0, 0), (0, 1)]],
                     S.Zero,
                     inequalities=[[[(0,0)]],
                                   [[(0,1)]]])
        lb_dependencies[nodes[X]].add(rule4)
        lb_dependencies[nodes[Y]].add(rule4)
        yield rule4

        # a <= 0, b >= 0, c <= 0, d >=0, ad <= bc => ad <= XY
        rule5 = Rule(nodes[res_monom],
                     RuleType.LB,
                     [nodes[X], nodes[Y]],
                     [nodes[X], nodes[Y]],
                     [[(0,0),(1,1)]],
                     S.Zero,
                     inequalities=[[[(0,0),(2,-S.One)]],
                                   [[(0,1),(2,-S.One)]],
                                   [[(1,0)]],
                                   [[(1,1)]],
                                   [[(0,1), (1,0),(2,-S.One)],[(0,0),(1,1)]]])
        lb_dependencies[nodes[X]].add(rule5)
        lb_dependencies[nodes[Y]].add(rule5)
        ub_dependencies[nodes[X]].add(rule5)
        ub_dependencies[nodes[Y]].add(rule5)
        yield rule5

        # a <= 0, b >= 0, c <= 0, d >=0, ad >= bc => bc <= XY
        rule6 = Rule(nodes[res_monom],
                     RuleType.LB,
                     [nodes[X], nodes[Y]],
                     [nodes[X], nodes[Y]],
                     [[(0,1),(1,0)]],
                     S.Zero,
                     inequalities=[[[(0,0),(2,-S.One)]],
                                   [[(0,1),(2,-S.One)]],
                                   [[(1,0)]],
                                   [[(1,1)]],
                                   [[(0,1), (1,0)],[(0,0),(1,1),(2,-S.One)]]])
        lb_dependencies[nodes[X]].add(rule6)
        lb_dependencies[nodes[Y]].add(rule6)
        ub_dependencies[nodes[X]].add(rule6)
        ub_dependencies[nodes[Y]].add(rule6)
        yield rule6

        

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
    for X, Y in product(monoms, monoms):
        if simplify(X*Y) not in monoms and simplify(Y*X) not in monoms:
            continue  # to high degree
        res_monom = simplify(X*Y) if simplify(X*Y) in monoms else simplify(Y*X)

        #  a <= X, a <= 0
        #  0 <= Y, E(Y) <= b
        rule1 = Rule(nodes[Expexted(res_monom)],
                     RuleType.LB,
                     [nodes[X], nodes[Y]],
                     [nodes[Expexted(Y)]],
                     [[(0, 0), (1, 0)]],
                     S.Zero,
                     inequalities=[[[(0,0),(2,-S.One)]],
                                   [[(0,1)]],
                                   [[(1,0)]]]) # last should follow from 2nd
        lb_dependencies[nodes[X]].add(rule1)
        lb_dependencies[nodes[Y]].add(rule1)
        ub_dependencies[nodes[Expexted(Y)]].add(rule1)
        yield rule1

        #  X <= a, a >= 0
        #  0 <= Y, E(Y) <= b, b Y= 0
        # ==> E(XY) <= ab
        rule2 = Rule(nodes[Expexted(res_monom)],
                     RuleType.UB,
                     [nodes[Y]],
                     [nodes[X], nodes[Expexted(Y)]],
                     [[(1,0), (1,1)]],
                     S.Zero,
                     inequalities=[[[(0,0)]],
                                   [[(1,1)]],
                                   [[(1,0)]]])
        lb_dependencies[nodes[Y]].add(rule2)
        ub_dependencies[nodes[X]].add(rule2)
        ub_dependencies[nodes[Expexted(Y)]].add(rule2)
        yield rule2

        #  a<=X, a <= 0
        #  0 <= Y, b <= E(Y), b >= 0
        # ==> E(XY) >= ab
        rule3 = Rule(nodes[Expexted(res_monom)],
                     RuleType.LB,
                     [nodes[X], nodes[Y],nodes[Expexted(Y)]],
                     [],
                     [[(0,0),(0,2)]],
                     S.Zero,
                     inequalities=[[[(0,0),(2,-S.One)]], # TODO: revise removing one positivity constraint in document
                                   [[(0,1)]],
                                   [[(0,2)]]]) # last should follow from previous
        lb_dependencies[nodes[X]].add(rule3)
        lb_dependencies[nodes[Y]].add(rule3)
        lb_dependencies[nodes[Expexted(Y)]].add(rule3)
        yield rule3


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
    expectation_symbols = {sym for sym in expression_map.free_symbols if str(
        sym).startswith("E(")}
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
                UB_coeffs.append([(1, len(UB_ub_values)), (2, coeff)])
                UB_ub_values.append(nodes[exp_term])
                ub_dependencies[nodes[exp_term]].add(ub_rule)

                LB_coeffs.append([(0, len(LB_lb_values)), (2, coeff)])
                LB_lb_values.append(nodes[exp_term])
                lb_dependencies[nodes[exp_term]].add(lb_rule)

                UB_i += 1
                LB_i += 1
            elif coeff.is_negative:
                UB_coeffs.append([(0, len(UB_lb_values)), (2, coeff)])
                UB_lb_values.append(nodes[exp_term])
                ub_dependencies[nodes[exp_term]].add(lb_rule)

                LB_coeffs.append([(1, len(LB_ub_values)), (2, coeff)])
                LB_ub_values.append(nodes[exp_term])
                lb_dependencies[nodes[exp_term]].add(ub_rule)

                UB_i += 1
                LB_i += 1
            else:
                raise ValueError(
                    "Coefficient must be number, hence sign must be known")
        yield ub_rule
        yield lb_rule
