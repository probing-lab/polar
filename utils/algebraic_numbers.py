from typing import List, Union
from sympy import AlgebraicNumber, primitive_element, floor, ln, Abs, Number, Expr


def algebraic_number_equals_const(x: Union[AlgebraicNumber, Expr], c: Union[Number, int]) -> bool:
    """
    Efficient function to determine whether x == c for an algebraic number x and a constant c
    The algebraic number can be given as Algebraic number or as an expression that is algebraic.
    The constant must be a number or an integer.
    """
    if x == 1:
        return True
    x = AlgebraicNumber(x)
    if x.minpoly.degree() == 1 and x.minpoly.LC() == 1 and x.minpoly.eval(c) == 0:
        return True
    return False


def faccin_height(x: AlgebraicNumber) -> Number:
    """
    Returns the height of an algebraic !integer! as defined by Faccin.
    http://eprints-phd.biblio.unitn.it/1182/ Definition 6.
    """
    poly = x.minpoly()
    M = poly.LC()
    roots = poly.all_roots(multiple=False)
    for root, mult in roots:
        M *= max(Abs(root), 1) ** mult
    return ln(M) / poly.degree()


def field_extension_degree(xs: List[AlgebraicNumber]) -> int:
    """
    Returns the dimension of the number field Q(xs) as a vectors space over Q.
    """
    irrationals = [x for x in xs if x.minpoly.degree() > 1]
    if len(irrationals) == 0:
        return 1
    extension_min_poly, _ = primitive_element([x for x in xs if x.minpoly.degree() > 1])
    return int(extension_min_poly.as_poly().degree())


def faccin_bound(xs: List[AlgebraicNumber]) -> int:
    """
    Returns a positive bound for the size of elements in the basis of the exponent lattice
    of the algebraic !integers! for n1,...,nk in ns all e1,...,ek in Z st.
    n1^e1 * ... * nk^ek = 1 forms a lattice on Z.
    This lattice has a basis b1,...,br with |bi| < faccin_bound for all bi

    The bound is from Faccin's Ph.D. thesis:
    http://eprints-phd.biblio.unitn.it/1182/ Definition 6.
    """

    h0 = max([faccin_height(x) for x in xs])
    if not h0.is_positive:
        h0 = ln(2)

    n = field_extension_degree(xs)
    if n >= 3:
        eta0 = ((ln(ln(n)) / ln(n)) ** 3) / 4*n
    else:
        eta0 = ln(1.17) / 2

    s = len(xs)
    R = s**(s-1) * (n + 1)**2 * (h0 / eta0)**(s-1)
    return int(floor(R))
