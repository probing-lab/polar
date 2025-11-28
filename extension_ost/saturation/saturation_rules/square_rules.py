from sympy import S, Add, Mul, Pow, Abs
from extension_ost.helpers import Expexted
from extension_ost.saturation.saturation_rules.rule import BoundRef, Rule, RuleType


def generate_square_rules(square_monoms,
                          monoms,
                          nodes,
                          lb_dependencies,
                          ub_dependencies):
    """Generates rules for deriving bounds

    Args:
        monoms (_type_): _description_
        nodes (_type_): _description_
        lb_dependencies (_type_): _description_
        ub_dependencies (_type_): _description_
    """
    for square_monom in square_monoms:
        # form (aX+bY)**2
        assert isinstance(square_monom, Expexted)
        expr_inner = square_monom.args[0]
        assert isinstance(expr_inner, Pow)
        assert expr_inner.args[1] == 2*S.One
        base = expr_inner.args[0]
        assert isinstance(base, Add) and len(base.args) == 2
        aX = base.args[0]
        bY = base.args[1]
        coeff1 = Mul(*[t for t in Mul.make_args(aX) if t.is_number])
        Var1 = Mul(*[t for t in Mul.make_args(aX) if not t.is_number])
        coeff2 = Mul(*[t for t in Mul.make_args(bY) if t.is_number])
        Var2 = Mul(*[t for t in Mul.make_args(bY) if not t.is_number])

        assert (coeff1*Var1+coeff2*Var2)**2 == expr_inner

        for (a, X, b, Y) in [(coeff1, Var1, coeff2, Var2), (coeff2, Var2, coeff1, Var1)]:
            assert a.is_number
            assert b.is_number
            # The rule is (through Minkowski inequality):
            # E((aX+bY)**2) <= u
            # E(X**2) <= v
            # ==============
            # E(Y**2) <= (1/(b**2) * u + 2* |a|/(b**2) * sqrt(u)*sqrt(v) + a**2/b**2*v)
            rule_ub = Rule(nodes[Expexted(Y**2)],
                           RuleType.UB,
                           lbs=[],
                           ubs=[nodes[square_monom] ,nodes[Expexted(X**2)]],
                           res_expr=[[(BoundRef.Const, 1/b**2), (BoundRef.UB, 0)],
                                     [(BoundRef.Const, 2*abs(a)/b**2), (BoundRef.Sqrt,(BoundRef.UB, 0)), (BoundRef.Sqrt,(BoundRef.UB, 1))],
                                     [(BoundRef.Const, a**2/b**2), (BoundRef.UB, 1)]],
                                     res_intercept=S.Zero) # those rules are cycle sensitive - hence prevent them
            ub_dependencies[nodes[square_monom]].add(rule_ub)
            ub_dependencies[nodes[Expexted(X**2)]].add(rule_ub)
            yield rule_ub