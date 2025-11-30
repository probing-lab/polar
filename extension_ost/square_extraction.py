from typing import Dict, Optional, Tuple
from sympy import S, Add, Expr, Mul, Pow, Symbol, rem, simplify, sqrt

from extension_ost.helpers import Expexted


def _sqroot_and_sign_if_possible(expr: Expr) -> Optional[Tuple[Expr, Expr]]:
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
        a = S.One
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
            
    return simplify(x),(a if a.is_nonnegative else -a), 1 if a.is_nonnegative else -1

def _factor_if_exists(expr: Expr, potential_factor: Expr) -> Optional[Expr]:
    """
    Args:
        expr (Expr): the expression for which it is checked, whether it is a square
    """
    if len(expr.free_symbols - potential_factor.free_symbols) == 0:
        return
    terms = Mul.make_args(potential_factor)
    a_given = Mul(*[t for t in terms if t.is_number])
    expected_given = Mul(*[t for t in terms if not t.is_number])
    if isinstance(expr, Mul):
            # assert len(expr.args) == 2
            a,expected = expr.as_coeff_Mul()
    elif isinstance(expr, Expexted):
        a = 1
        expected = expr
    else:
        return
    assert isinstance(expected, Expexted)

    if rem(expected.args[0], expected_given) == S.Zero:
        # is a true factor
        return a/a_given*expected.args[0]/expected_given


def reformulate_with_squares(expression_map: Expr, monom_maps: Dict[Expr, Expr]):
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
    monom_maps_inv = {v:Symbol(k) for k, v in monom_maps.items()}
    plus_terms = [expression_map] if not isinstance(expression_map, Add) else expression_map.args

    roots_of_squares = [v for t in plus_terms if (v:=_sqroot_and_sign_if_possible(t))]
    
    maps = []
    for monom_root, coeff, sign in roots_of_squares:
        if len(monom_root.free_symbols)==0:
            continue       
        expression_map_adapted = simplify(expression_map/coeff)
        plus_terms = [expression_map_adapted] if not isinstance(expression_map_adapted, Add) else expression_map_adapted.args

        factors = [v for t in plus_terms if (v:=_factor_if_exists(t, 2*monom_root*sign))]
        pass
        for factor in factors:
            if len(factor.free_symbols) == 0:
                continue
            # check if factor squared is still permissible
            if any(exp_atom not in set(monom_maps.values()) for exp_atom in simplify(Expexted(factor**2)).atoms(Expexted)):
                continue

            expression = Expexted((monom_root + factor)**2)

            new_expression_map = simplify(expression_map_adapted - sign*expression)
            new_expression_map_E = new_expression_map.subs(monom_maps_inv)
            new_expression_map_with_square = new_expression_map_E +sign* Symbol(f"E({(monom_root+factor)**2})")
            maps.append((new_expression_map_with_square, {Symbol(f"E({(monom_root+factor)**2})"): Expexted((monom_root+factor)**2, evaluate=False)}))

    maps_to_return=list()
    for map in maps:
        _, monom_dict = map
        duplicate = False
        for m in maps_to_return:
            if rem(list(monom_dict.values())[0].args[0],list(m[1].values())[0].args[0]) == S.Zero:
                duplicate=True
                break
        if not duplicate:
            maps_to_return.append(map)
    yield from maps_to_return
    
def reformulate_maps_with_squares(expression_maps: Expr, monom_maps: Dict[Expr, Expr]):
    maps = []
    for map in expression_maps:
        maps += reformulate_with_squares(map, monom_maps)

    return maps
