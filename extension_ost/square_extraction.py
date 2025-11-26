from typing import Optional, Tuple
from sympy import S, Add, Expr, Mul, Pow

from extension_ost.helpers import Expexted


def _sqroot_if_possible(expr: Expr) -> Optional[Expr]:
    """
    Given an expression of form a*Expexted(x^alpha) this function determins, whether
    the expression is a square of some other monomial

    Args:
        expr (Expr): the expression for which it is checked, whether it is a square
    """
    if isinstance(expr, Mul):
        # assert len(expr.args) == 2
        a,expected = expr.as_coeff_Mul()
    elif isinstance(expr, Expexted):
        a = 1
        expected = expr
    else:
        return
    assert isinstance(expected, Expexted)

    mult_terms = [expected.args[0]] if not isinstance(expected.args[0], Mul) else expected.args[0].args

    x = S.One
    for mult_term in mult_terms:
        if isinstance(mult_term, Pow):
            base = mult_term.args[0]
            exponent = mult_term.args[1]
            if exponent.is_even:
                x *= base**(exponent/2)
        else:
            return
            
    return x*a


def reformulate_with_squares(expression_map: Expr, monom_maps: Expr):
    """
        Currently this method only works for extracting squares of the form 
        E((a*x+b*y)^2) from an expression, where a,b are (rational?) coefficients, whiel x and y are RVs.
        It could probably be generalized to higher powers, and to more complex polynomials as the base.
        
        It works by finding at least two of the subterms:
        (a*x+b*y)^2 = E(a^2x^2) + E(2abxy) + E(b^2y^2)

        It is useful, because sometimes in order to obtain a bound for E(b^2), 
        one needs a bound for E(ab) and vice versa
    """
    expression_map = expression_map.subs(monom_maps)
    plus_terms = [expression_map] if not isinstance(expression_map, Add) else expression_map.args

    roots_of_squares = [v for t in plus_terms if (v:=_sqroot_if_possible(t))]
    pass
    
def reformulate_maps_with_squares(expression_maps: Expr):
    maps = []
    for map in expression_maps:
        maps += reformulate_with_squares(map)

    return maps