r"""
Integer relations

This class provides methods to compute a basis of the exponent lattice
        
.. MATH::
    \{(e_1,\dots,e_n) \in \mathbb{Z}^n \colon x_1^{e_1} \dots x_n^{e_n}=1\}
    
of a tuple of algebraic numbers `x=(x_1,\dots,x_n)`. If the algebraic numbers
`x` are rational integers, a method based on factorizing these rational numbers
is used. For general algebraic numbers two methods, both based on LLL and a
bound on the basis, are implemented. 
    
EXAMPLES::

    sage: from rec_sequences.IntegerRelations import *
    
    sage: IntegerRelations.integer_relations([2,-1])
    [0 2]
    
    sage: IntegerRelations.integer_relations([3])
    []
    
    sage: numbers = [2^(1/2), (-2)^(1/3), I, -I]
    sage: relations = IntegerRelations.integer_relations(numbers)
    sage: relations.nrows()
    3
    sage: all([prod(xi**ei for xi, ei in zip(numbers, relation))==1 
    ....:                    for relation in relations])  
    True
            

    
"""
#############################################################################
# Copyright (C) 2022 Philipp Nuspl, philipp.nuspl@jku.at
#
# This program is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by the Free 
# Software Foundation, either version 3 of the License, or (at your option) 
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT 
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for 
# more details.
#
# You should have received a copy of the GNU General Public License along 
# with this program. If not, see <https://www.gnu.org/licenses/>. 
#############################################################################

from sage.all import *
from sage.matrix.special import identity_matrix
from sage.matrix.constructor import matrix
from sage.modules.free_module_element import vector
from sage.rings.rational_field import QQ
from sage.rings.qqbar import QQbar, number_field_elements_from_algebraics
from sage.rings.integer_ring import ZZ
from sage.rings.imaginary_unit import I
from sage.rings.complex_interval_field import ComplexIntervalField
from sage.symbolic.ring import SR
from sage.symbolic.constants import pi
from sage.misc.functional import sqrt, log, numerical_approx
from sage.misc.flatten import flatten
from sage.misc.misc_c import prod
from sage.functions.other import ceil, real_part, imag_part, floor
from sage.arith.functions import lcm
from sage.arith.misc import factor

class IntegerRelations :

    @staticmethod
    def _add_columns_to_matrix(M, columns, positions) :
        r"""
        Adds given columns to a matrix.
        
        INPUT:
        
        - ``M`` -- a matrix
        - ``columns`` -- either a matrix where the rows are interpreted 
          as the columns that are added or a list of vectors or
          a list of lists
        - ``positions`` -- a list of unique positions where the
          given columns should be in the new matrix 
        
        OUTPUT:
        
        A matrix which is obtained by inserting the given columns at the 
        specified positions in the given matrix ``M``.
        """
        M_new = matrix(M.base_ring(), M.nrows(), M.ncols() + len(positions))
        col_M = 0
        for i in range(M_new.ncols()) :
            if i in positions :
                M_new.set_column(i, columns[positions.index(i)])
            else :
                M_new.set_column(i, M.column(col_M))
                col_M += 1
        return M_new

    @staticmethod
    def _zero_check(a, certainty=100) :
        r"""
        Given a number ``a`` checks whether it is zero. This is done by first
        using the ``is_zero`` method. If it fails, the numerical approximation
        with ``certainty`` many digits is computed and it is checked whether
        it is zero.
        
        INPUT:
        
        - ``a`` -- a number
        
        OUTPUT:
        
        ``True`` if ``a`` is zero and ``False`` otherwise. This is not 
        necessarily checked symbolic and might be a numerical check.
        """
        try :
            return a.is_zero()
        except TypeError :
            return numerical_approx(a, digits=certainty) == 0
    
    @staticmethod 
    def _rational_approximation(cont_frac, min_level, error) :
        r"""
        Given a number `a` compute a rational approximation `b` such that
        `|b-a|<e` where `e` is the given ``error``.
        
        INPUT:

        - ``error`` -- a positive real number

        OUTPUT:

        A rational number which approximates the input ``a`` and the error
        bound which was computed.
        """
        if IntegerRelations._zero_check(cont_frac.value()) :
            return QQ(0), -1
        elif cont_frac.value() in QQ :
            return QQ(cont_frac.value()), -1
        
        max_error = lambda n : 1/(cont_frac.denominator(n)*\
                                  cont_frac.denominator(n+1))
        current_max_error = max_error(min_level)
        while current_max_error >= error :
            min_level += 1 
            current_max_error = max_error(min_level)
            
        return cont_frac.convergent(min_level), min_level
        
    @staticmethod 
    def _p_rational_approximation(x, p, error=1) :
        r"""
        vector x, p, error natural number
        Given a vector of numbers `x` computes a rational approximation `b`.
        
        INPUT:

        - ``x`` -- a vector of numbers
        - ``p`` -- a number
        - ``error`` (default: ``1``) -- a natural number

        OUTPUT:

        A rational approximation of the vector ``x``
        """
        R = x.parent()
        return R([round(p**error*xi, ndigits=1)/p**error for xi in x])
        
    @staticmethod
    def _check_basis(x, basis, approxs=-1) :
        r"""
        Given a list of algebraic numbers `x_1,\dots,x_n` checks whether the 
        given every element `e_1,\dots,e_n` in the given basis satisfies
        `x_1^{e_1} \cdots x_n^{e_n}=1`.
        
        INPUT:
        
        - ``x`` -- a list of algebraic numbers
        - ``basis`` -- an integer matrix where the rows represent the basis
          elements of a lattice (or a list of vectors). If the matrix has
          too many columns, the last columns are ignored.
          
        OUTPUT:
        
        ``True`` if all basis elements satisfy the equation and ``False`` 
        otherwise.
        """
        if approxs != -1 :
            # do a quick check with the given approximations
            basis = basis.matrix_from_columns(list(range(len(x))))
            for b in basis.rows() :
                power_prod = prod(xi**bi for xi, bi in zip(approxs, b))
                if not (power_prod-1).contains_zero() :
                    # power_prod is certainly not 1
                    return False 
            
        basis = basis.matrix_from_columns(list(range(len(x))))
        for b in basis.rows() :
            if prod(xi**bi for xi, bi in zip(x, b)) != 1 :
                return False 
        return True
    
    @staticmethod
    def _degree_extension(x) :
        r"""
        Given a list of algebraic numbers, returns the degree of the 
        extension field that contains all of them.
        
        INPUT:
        
        - ``x`` -- a list of algebraic numbers
        
        OUTPUT:
        
        The degree of the number field containing all algebraic numbers 
        in ``x``.
        """
        K, _, _ = number_field_elements_from_algebraics(x)
        return K.degree()
        
    @staticmethod 
    def _height(a) :
        r"""
        Computes the height of an algebraic integer as defined
        by Faccin.
        
        INPUT:
        
        - ``a`` -- an algebraic integer
        
        OUTPUT:
        
        The height of ``a``.
        """
        f = a.minpoly()
        d = a.degree()
        
        M = f.leading_coefficient()
        for root, mult in f.roots(ring=ComplexIntervalField(), 
                                  multiplicities=True) :
            M = M*(max(1, root.abs().upper())**mult)
        
        return log(M)/d
        
    @staticmethod 
    def _masser_bound(x, degree = -1) :
        r"""
        Given a list of algebraic integers, computes the bound by Masser
        which bounds the integer relations of the given algebraic numbers.
        We assume that the algebraic numbers are not all rational.
        
        INPUT:
        
        - ``x`` -- a list of algebraic numbers
        - ``degree`` (default: ``-1``) -- if the degree of the extension
          field is already known, it can be specified here. If the value
          is negative it will be computed.
        
        OUTPUT:
        
        The Masser bound of the algebraic numbers ``x``.
        """
        height = IntegerRelations._height
        
        h0 = max(height(xi) for xi in x)
        if h0 <= 0 :
            h0 = log(2)
            
        if degree < 0 :
            n = IntegerRelations._degree_extension(x)
        else :
            n = degree 
            
        if n >= 3 :
            etha0 = (log(log(n))/log(n))**3/(4*n)
        elif n==2 :
            etha0 = log(1.17)/2
        else :
            raise ValueError(f"Algebraic numbers cannot all be rational")
        
        s = len(x)
        R = s**(s-1)*(n+1)**2*(h0/etha0)**(s-1)
        return ceil(R)
    
    @staticmethod 
    def _to_algebraic_integer(a) :
        r"""
        Checks if a given algebraic number is an algebraic integer
        and gives the representation as such.
        
        INPUT:
        
        - ``x`` -- an algebraic number
        
        OUTPUT:
        
        A triple of the form ``flag, b, i`` where ``flag`` is
        ``True`` if ``a`` is an algebraic integer and false otherwise.
        ``b`` is an algebraic integer and ``i`` an integer such that 
        ``a==b/i``.
        
        EXAMPLES::
        
            sage: from rec_sequences.IntegerRelations import *
            
            sage: IntegerRelations._to_algebraic_integer(QQbar(17/13))
            (False, 17, 13)
            sage: IntegerRelations._to_algebraic_integer(I)
            (True, I, 1)
            sage: IntegerRelations._to_algebraic_integer(-I/2)
            (False, -2*I, 4)
            
        """
        f = a.minpoly()
        coeffs = f.coefficients()
        
        denoms = [coeff.denominator() for coeff in coeffs]
        common_denom = lcm(denoms)
        M = f.leading_coefficient()*common_denom 
        
        if M == 1 or M == - 1:
            return True, M*a, M
        else :
            return False, M*a, M
        
    @staticmethod 
    def integer_relations(x, integral = False) :
        r"""
        Computes all possible integer relations of the given algebraic numbers.
        If the input is rational, then a method based on factorizing the input
        is used. Otherwise one of two algorithms can be used:
        
        1) Kauers: An iterative algorithm based on LLL.
        2) Ge: Ge's original algorithm together with a result by Masser as 
           explained in detail in [F14]_.
        
        INPUT:
        
        - ``x`` -- a list of algebraic numbers
        - ``integral`` (default: ``False``) -- if ``True`` it will be assumed 
          that all elements of ``x`` are algebraic integers
        
        OUTPUT:
        
        Let `x=(x_1,\dots,x_n)`. Returns a basis for the lattice of relations
        
        .. MATH::
            \{(e_1,\dots,e_n) \in \mathbb{Z}^n \colon x_1^{e_1} \dots x_n^{e_n}=1\}
        
        The basis is returned as the rows of a matrix over ``Z``.
       
        EXAMPLES::
        
            sage: from rec_sequences.IntegerRelations import *
            
            sage: IntegerRelations.integer_relations([-1])
            [2]
            sage: IntegerRelations.integer_relations([I,0,-I])
            [ 1  0  1]
            [-2  0  2]
            sage: IntegerRelations.integer_relations([1,-1,2])
            [1 0 0]
            [0 2 0]
            
        """
        if len(x) == 0 :
            return matrix(QQ, 0, 0)
        
        x = [QQbar(xi) for xi in x]
        n = len(x)

        # make sure that only nonzero x are given
        zero_indices = [i for i, xi in enumerate(x) if xi.is_zero()]
        if len(zero_indices) > 0 :
            non_zero_x = [xi for xi in x if not xi.is_zero()]
            relations = IntegerRelations.integer_relations(non_zero_x, 
                                                           algorithm=algorithm,
                                                           integral=integral)
            zero_matrix = matrix(ZZ, len(zero_indices), relations.nrows())
            relations = IntegerRelations._add_columns_to_matrix(relations, 
                                                               zero_matrix, 
                                                               zero_indices)
            return relations
        
        # make sure that we only deal with algebraic integers
        to_algebraic_integer = IntegerRelations._to_algebraic_integer
        if not integral :
            x_integral = [to_algebraic_integer(xi) for xi in x]
            are_integral = [integral_rep[0] for integral_rep in x_integral]
            if not all(are_integral) :
                new_x = [integral_rep[1] for integral_rep in x_integral]
                denoms_x = [integral_rep[2] for integral_rep in x_integral]
                basis = IntegerRelations.integer_relations(new_x+denoms_x,
                                                           integral=True)
                restrict = identity_matrix(ZZ,n).augment(-identity_matrix(ZZ,n))
                L = ZZ**(2*n)
                M_basis = L.submodule_with_basis(basis)
                M_restrict = L.submodule_with_basis(restrict)
                B = M_basis.intersection(M_restrict).matrix()
                return B.matrix_from_columns(list(range(n)))
            
        if all([xi in ZZ for xi in x]) :
            return IntegerRelations.integer_relations_integers(x)
        else :
            return IntegerRelations.integer_relations_kauers(x)

    @staticmethod
    def integer_relations_integers(x):
        r"""
        Computes all possible integer relations of the given integer numbers.
        
        INPUT:
        
        - ``x`` -- a list of integers 
        
        OUTPUT:
        
        Let `x=(x_1,\dots,x_n)`. Returns a basis for the lattice of relations
        
        .. MATH::
            \{(e_1,\dots,e_n) \in \mathbb{Z}^n \colon x_1^{e_1}\dots x_n^{e_n}=1\}
        
        The basis is returned as the rows of a matrix over ``Z``.
       
        EXAMPLES::
        
            sage: from rec_sequences.IntegerRelations import *
            
            sage: IntegerRelations.integer_relations_integers([-1])
            [2]
            sage: IntegerRelations.integer_relations_integers([-3,3,2,1])
            [ 2 -2  0  0]
            [ 0  0  0  1]
            sage: IntegerRelations.integer_relations_integers([1,-1,2])
            [1 0 0]
            [0 2 0]
            
        """
        factors = [factor(ZZ(xi)) for xi in x]
        primes = list(set(flatten([[factorj for factorj, _ in factors_xi] 
                                               for factors_xi in factors])))
        M = matrix(ZZ, len(primes)+1, len(x)+1)
        for i, prime in enumerate(primes) :
            for j, factorj in enumerate(factors) :
                num_factors = 0
                for prime_factor, mult in factorj :
                    if prime_factor == prime :
                        num_factors = mult 
                        break
                M[i,j] = num_factors
        
        # negative signs have to sum up to multiple of two 
        last_row = len(primes)
        for j, factorj in enumerate(factors) :
            if factorj.unit() == -1 :
                M[last_row, j] = 1
        M[last_row, len(x)] = 2
        
        ker = M.right_kernel().matrix()
        # get rid of last column, which accounts for sign 
        return ker.matrix_from_columns(list(range(len(x))))
        
        
    @staticmethod 
    def integer_relations_kauers(a, precision=100) :
        r"""
        Computes all possible integer relations of the given algebraic integers.
        This is based on Ge's algorithm as outlined in the PhD thesis of
        Manuel Kauers.
        
        INPUT:
        
        - ``a`` -- a list of non-zero algebraic integers, not all integral
        - ``precision`` (default: ``100``) -- to check if certain vectors really
          give rise to integer relations, numerical checks with this precision 
          are made before doing the symbolic check.
        
        OUTPUT:
        
        Let `a=(a_1,\dots,a_n)`. Returns a basis for the lattice of relations
        
        .. MATH::
            \{(e_1,\dots,e_n) \in \mathbb{Z}^n \colon a_1^{e_1}\dots a_n^{e_n}=1\}
        
        The basis is returned as the rows of a matrix over ``Z``.
       
        EXAMPLES::
        
            sage: from rec_sequences.IntegerRelations import *
            
        """
        approximate = IntegerRelations._p_rational_approximation
        
        K = ComplexIntervalField(prec=precision)
        approxs = [K(ai) for ai in a]
        x = vector(SR, [log(ai) for ai in a]+[2*pi*I])
        real_parts = vector(SR, [real_part(xi) for xi in x])
        imgs_parts = vector(SR, [imag_part(xi) for xi in x])
        
        n = len(x)
        K, a_K, _ = number_field_elements_from_algebraics(a)
        M = IntegerRelations._masser_bound(a, degree=K.degree()) 
        w = 1
        B = identity_matrix(QQ, n).augment(matrix(QQ, n, 2))
        xi_real, xi_imag = vector(QQ, n), vector(QQ, n)
        
        while not IntegerRelations._check_basis(a_K, B, approxs) :
            w = 2*w 
            error = n*w
            
            # improve approximations 
            xi_real = approximate(real_parts, error)
            xi_imag = approximate(imgs_parts, error)
                    
            # replace vectors 
            for j, b in enumerate(B.rows()) :
                e = b[:n]
                B[j,n] = w*(e*xi_real)
                B[j,n+1] = w*(e*xi_imag)
            
            B = B.LLL()
            B_bar = B.gram_schmidt()[0]
            r = B.nrows()
            while r > 0 and B_bar.row(r-1).norm(2) > sqrt(n+2)*M:
                r = r-1
            B = B.matrix_from_rows(list(range(r)))
                    
        return matrix(ZZ, B.matrix_from_columns(list(range(len(a)))))

def to_algebraic_number(expr: str):
    expr = sympify(expr)
    if isinstance(expr, CRootOf):
        interval = expr._get_interval()
        if expr.is_real:
            real_from = Rational(str(interval.a))._sage_()
            real_to = Rational(str(interval.b))._sage_()
            sage_interval = RIF(real_from, real_to)
        else:
            real_from = Rational(str(interval.ax))._sage_()
            real_to = Rational(str(interval.bx))._sage_()
            im_from = Rational(str(interval.ay))._sage_()
            im_to = Rational(str(interval.by))._sage_()
            sage_interval = CIF(RIF(real_from, real_to), RIF(im_from, im_to))

        min_poly = polynomial(expr.expr._sage_(), base_ring=QQ)
        return QQbar.polynomial_root(min_poly, sage_interval)

    return QQbar(expr._sage_())



if __name__ == "__main__":
    import sys
    from sympy import sympify, CRootOf
    from sage.symbolic.expression_conversions import polynomial
    import json
    import warnings

    warnings.filterwarnings("ignore")

    numbers = [to_algebraic_number(n) for n in sys.argv[1:]]
    result = IntegerRelations.integer_relations(numbers)
    print(json.dumps(result.numpy().tolist()))
