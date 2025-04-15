from typing import Optional
from sympy import Eq, Poly, Symbol, S, smtlib_code

from termination.smt.smt_formula import SMTFormula
from termination.util.enums import LogicalState, TerminationProperty


class SMTTerminationCondition:
    def __init__(
        self,
        poly: Poly,
        terminates_zero: bool,
        terminates_negative: bool,
        has_prolog: bool,
    ) -> None:
        self.poly = poly
        self.terminates_zero = terminates_zero
        self.terminates_negative = terminates_negative
        self.has_prolog = has_prolog

    def get_smt_formula(self) -> Optional[SMTFormula]:
        if self.has_prolog:
            print("SMT termination only supports loops without a prolog.")
            return None
        elif not self.terminates_negative:
            print(
                "SMT termination only supports eventual/asymptotical nontermination, not termination on exact value."
            )
            return None

        n = Symbol("n")
        poly = Poly(self.poly, n)
        print(f"Analyzing polynomial: {poly}")
        coeff_vars = []
        smt_exprs = []
        final_assertion = S.false
        for i, coeff in enumerate(poly.coeffs()):
            sym = Symbol(f"alpha_{i}")
            smt_exprs.append(Eq(sym, coeff))

            term = sym > 0
            for var in coeff_vars:
                term = term & (Eq(var, 0))
            final_assertion = final_assertion | term
            coeff_vars.append(sym)
        smt_exprs.append(final_assertion)
        smt_formula = smtlib_code(smt_exprs)
        smt_formula = smt_formula.replace("pow", "^")
        return SMTFormula(
            smt_formula,
            [
                (LogicalState.Sat, TerminationProperty.Nontermination),
                (LogicalState.Unsat, TerminationProperty.Terminating),
            ],
        )
