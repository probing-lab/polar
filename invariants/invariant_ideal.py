from typing import Set, Dict
from sympy import Expr, Symbol, Pow, groebner, numer, denom

from invariants.exceptions import InvariantIdealException
from utils import unpack_piecewise, get_unique_var, are_coprime

ClosedForm = Expr
ExponentBase = Expr


class InvariantIdeal:

    closed_forms: Dict[Symbol, ClosedForm]
    base_to_symbol: Dict[Expr, Symbol]
    n: Symbol

    def __init__(self, closed_forms: Dict[str, ClosedForm]):
        self.n = Symbol("n", integer=True)
        self.closed_forms = {}
        for goal, expr in closed_forms.items():
            variable = Symbol(goal)
            self.closed_forms[variable] = unpack_piecewise(expr).expand().powsimp().expand()
        self.base_to_symbol = {}
        for s, cf in self.closed_forms.items():
            self.closed_forms[s] = self.abstract_exponentials(cf)

    def compute_basis(self) -> Set[Expr]:
        polys = [s - cf for s, cf in self.closed_forms.items()]
        polys = polys + self.get_algebraic_relations_exponentials()
        # n > variables abstracting exponentials > goal variables
        symbols = [self.n] + list(self.base_to_symbol.values()) + list(self.closed_forms.keys())
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
        exponent, the exponent must be equal to n.
        The method modifies the self.base_to_symbol, to store and reuse the symbols used for the bases.
        Example:
            "n**2 + n*2**n - 3**n + 2**n" returns
            "n**2 + n*a - b + a"
        """
        # Modify powers with n in exponent
        if isinstance(expression, Pow) and self.n in expression.args[1].free_symbols:
            base = expression.args[0]
            exponent = expression.args[1]
            if not base.is_Number:
                raise InvariantIdealException(f"The base of every exponential in n must be a number, but got {base}.")
            if exponent != self.n:
                raise InvariantIdealException(f"The exponent of every exponential in n must be equal to n, but got {exponent}")
            if base not in self.base_to_symbol:
                self.base_to_symbol[base] = Symbol(get_unique_var("b"))
            return self.base_to_symbol[base]

        if not expression.args:
            return expression

        new_args = [self.abstract_exponentials(a) for a in expression.args]
        return expression.func(*new_args)

    def get_algebraic_relations_exponentials(self):
        if len(self.base_to_symbol) <= 1:
            return []
        bases = self.base_to_symbol.keys()
        all_rational = all([b.is_Rational for b in bases])
        if all_rational:
            integers = [numer(b) for b in bases if numer(b) != 1]
            integers += [denom(b) for b in bases if denom(b) != 1]
            if are_coprime(integers):
                return []
            # Implement algebraic relations for rationals
            raise NotImplementedError()
        # Implement algebraic relations for algebraic numbers
        raise NotImplementedError()
