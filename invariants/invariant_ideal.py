from typing import Set, Dict
from sympy import Expr, Symbol, Pow, Mul, groebner

from invariants.exceptions import InvariantIdealException
from invariants.exponent_lattice import ExponentLattice
from invariants.lattice_ideal import LatticeIdeal
from utils import unpack_piecewise, get_unique_var

ClosedForm = Expr
ExponentBase = Expr


class InvariantIdeal:
    """
    This class represents the ideal of all polynomial invariants among program variables given their
    closed-form solutions (exponential polynomials in n).
    The class provides a method to compute a finite basis for this ideal.
    It follows the procedure of https://www.sciencedirect.com/science/article/pii/S074771710800045X
    """

    closed_forms: Dict[Symbol, ClosedForm]
    base_to_symbol: Dict[ExponentBase, Symbol]
    n: Symbol

    def __init__(self, closed_forms: Dict[str, ClosedForm]):
        self.n = Symbol("n", integer=True)
        self.closed_forms = {}
        for goal, expr in closed_forms.items():
            variable = Symbol(goal)
            self.closed_forms[variable] = (
                unpack_piecewise(expr).expand().powsimp().expand()
            )
        self.base_to_symbol = {}
        for s, cf in self.closed_forms.items():
            self.closed_forms[s] = self.abstract_exponentials(cf)

    def compute_basis(self) -> Set[Expr]:
        """
        Computes a finite basis for the ideal of all polynomial relations among the given closed-forms.
        """
        # Closed-form polynomials
        polys = [s - cf for s, cf in self.closed_forms.items()]

        # Add algebraic relations among the geometric sequences given by the exponentials in the closed-forms
        exponent_bases = list(self.base_to_symbol.keys())
        exponent_symbols = list(self.base_to_symbol.values())
        exponent_lattice = ExponentLattice(exponent_bases)
        lattice_ideal = LatticeIdeal(exponent_lattice.compute_basis(), exponent_symbols)
        polys = polys + list(lattice_ideal.compute_basis())

        # n > variables abstracting exponentials > goal variables --> we want to compute an elimination ideal
        symbols = (
            [self.n]
            + list(self.base_to_symbol.values())
            + list(self.closed_forms.keys())
        )
        cf_basis = groebner(polys, *symbols)

        basis = set()
        forbidden_vars = set(self.base_to_symbol.values()) | {self.n}
        for expr in cf_basis:
            if not forbidden_vars & expr.free_symbols:
                basis.add(expr)
        return basis

    def abstract_exponentials(self, expression: Expr):
        """
        Given an expression e, the method replaces exponentials of n in e by fresh variables.
        The function returns the modified expression.
        Important: The given expression must be expanded such that for all exponentials in the expression with n in its
        exponent, the exponent must be equal to C*n for some constant C.
        The method modifies the self.base_to_symbol, to store and reuse the symbols used for the bases.
        Example:
            "n**2 + n*2**n - 3**n + 2**n" returns
            "n**2 + n*a - b + a"
        """
        # Modify powers with n in exponent
        if isinstance(expression, Pow) and self.n in expression.args[1].free_symbols:
            base = expression.args[0]
            exponent = expression.args[1]

            # if expression is base ** (C*n) convert it to (base**C) ** n
            if isinstance(exponent, Mul):
                factor1 = exponent.args[0]
                factor2 = exponent.args[1]
                if factor1 == self.n:
                    base = base**factor2
                    exponent = self.n
                elif factor2 == self.n:
                    base = base**factor1
                    exponent = self.n

            if not base.is_number:
                raise InvariantIdealException(
                    f"The base of every exponential in n must be a number, but got {base}."
                )
            if exponent != self.n:
                raise InvariantIdealException(
                    f"The exponent of every exponential in n must be equal to n, but got {exponent}"
                )
            if base not in self.base_to_symbol:
                self.base_to_symbol[base] = Symbol(get_unique_var("b"))
            return self.base_to_symbol[base]

        if not expression.args:
            return expression

        new_args = [self.abstract_exponentials(a) for a in expression.args]
        return expression.func(*new_args)
