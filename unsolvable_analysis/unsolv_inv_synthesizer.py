from typing import Union
from utils import get_unique_var, solve_rec_by_summing, get_terms_with_vars, get_monoms
from symengine.lib.symengine_wrapper import Symbol
from sympy import sympify, Number, linsolve, nonlinsolve
from recurrences import RecBuilder
from program import Program
from recurrences.solver import RecurrenceSolver


class UnsolvInvSynthesizer:
    """
    Generates all possible polynomial invariants with some given variables upto a fixed degree
    In essence the class follows the procedure described in our paper
    "Solving Invariant Generation for Unsolvable Loops".
    Additionally, the class has the functionality of finding invariants for a fixed "k" (then all equations are linear).
    """

    @classmethod
    def __get_candidate_terms__(cls, pos, vars, deg, pw, s):
        if pos == len(vars):
            if s == 0:
                return 0, {0}
            term = 1
            for i in range(pos):
                term = term * (vars[i] ** pw[i])
            coeff = Symbol(get_unique_var())
            term = coeff * term
            return term, {coeff}
        ans = 0
        coefficients = set()
        for i in range(deg + 1):
            if s + i <= deg:
                pw[pos] = i
                expr, c = cls.__get_candidate_terms__(pos + 1, vars, deg, pw, s + i)
                if expr == 0:
                    continue
                ans += expr
                for elem in c:
                    coefficients.add(elem)
        return (
            ans,
            coefficients,
        )

    @classmethod
    def __get_candidate__(cls, vars, deg):
        ans, coeffs = cls.__get_candidate_terms__(0, vars, deg, [0] * len(vars), 0)
        return ans, coeffs

    @classmethod
    def __get_effective_monoms__(cls, candidate_rec, defective_variables, variables):
        result = set()
        monoms = get_terms_with_vars(candidate_rec, variables)[0]
        index_to_vars = {i: var for i, var in enumerate(variables)}
        for monom, coeff in monoms:
            defective = False
            term = 0
            for i in range(len(monom)):
                if monom[i] == 0:
                    continue
                cur_var = index_to_vars[i]
                if cur_var in defective_variables:
                    defective = True
                term += cur_var ** monom[i]
            if not defective and sum(monom) > 0:
                result.add(term)
        return result

    @classmethod
    def __get_effective_poly__(cls, good_set):
        """
        Construct the polynomial with effective monomials representing the sigma on rhs of Eq. (3) in the SAS paper
        """
        poly = 0
        symbols = set()
        for term in good_set:
            coeff = Symbol(get_unique_var())
            symbols.add(coeff)
            poly += coeff * term

        coeff = Symbol(get_unique_var())
        symbols.add(coeff)
        poly += coeff
        return poly, symbols

    @classmethod
    def __get_init_value_candidate__(cls, candidate, rec_builder):
        """
        Computes the initial value of the candidate (0'th iteration, i.e., before loop).
        """
        ans = 0
        monoms = get_monoms(candidate, rec_builder.program.variables)
        for monom, coeff in monoms:
            ans += rec_builder.get_initial_value(monom) * coeff
        return ans

    @classmethod
    def __construct_equations__(
        cls,
        candidate_rec,
        candidate_coefficients,
        kcandidate,
        rhs_effective_part,
        effective_part_coeffs,
        k,
    ):
        """
        Constructs system of equations derived from main equation (Eq. (3) in paper) for feeding into SymPy.
        """
        candidate_rec_monoms = get_monoms(
            candidate_rec, candidate_coefficients, with_constant=True
        )
        kcandidate_monoms = get_monoms(
            kcandidate, candidate_coefficients | {k}, with_constant=True
        )
        good_part_monoms = get_monoms(
            rhs_effective_part, effective_part_coeffs, with_constant=True
        )
        equation_terms = {}
        for coeff, monom in candidate_rec_monoms:
            equation_terms[monom] = equation_terms.get(monom, 0) + coeff
        for coeff, monom in kcandidate_monoms:
            equation_terms[monom] = equation_terms.get(monom, 0) - coeff
        for coeff, monom in good_part_monoms:
            equation_terms[monom] = equation_terms.get(monom, 0) - coeff
        equations = []
        for eq in equation_terms.values():
            equations.append(eq)
        return equations

    @classmethod
    def __solve_effective_part__(
        cls,
        rhs_effective_part,
        effective_part_coeffs,
        numeric_roots,
        numeric_croots,
        numeric_eps,
        program,
    ):
        """
        Fina a closed form for the summation in Eq. (3) with respect to n and initial values.
        """
        effective_part_monoms = get_monoms(
            rhs_effective_part, effective_part_coeffs, with_constant=True
        )
        effective_part_solution = 0
        for coeff, monom in effective_part_monoms:
            if monom == 1:
                effective_part_solution += coeff
                continue
            rec_builder = RecBuilder(program)
            recs = rec_builder.get_recurrences(monom)
            rec_solver = RecurrenceSolver(
                recurrences=recs,
                numeric_roots=numeric_roots,
                numeric_croots=numeric_croots,
                numeric_eps=numeric_eps,
            )
            effective_part_solution += coeff * rec_solver.get(monom)
        effective_part_solution = effective_part_solution.xreplace(
            {sympify("n"): sympify("n") - 1}
        )
        return effective_part_solution

    @classmethod
    def construct_candidate(cls, candidate_vars, inv_deg, program):
        candidate, candidate_coefficients = cls.__get_candidate__(
            candidate_vars, inv_deg
        )
        rec_builder = RecBuilder(program)
        candidate_rec = rec_builder.get_recurrence_poly(candidate, candidate_vars)
        return candidate, candidate_rec, candidate_coefficients

    @classmethod
    def construct_inhomogeneous_part(
        cls, candidate_rec, defective_variables, variables
    ):
        effective_monoms = cls.__get_effective_monoms__(
            candidate_rec, defective_variables, variables
        )
        rhs_effective_part, effective_coeffs = cls.__get_effective_poly__(
            effective_monoms
        )
        return rhs_effective_part, effective_coeffs

    @classmethod
    def construct_homogenous_part(cls, candidate, k: Union[Number, int, None] = None):
        if k is None:
            k = Symbol(get_unique_var("k"), nonzero=True)
        kcandidate = (k * candidate).expand()
        return k, kcandidate

    @classmethod
    def solve_quadratic_system(
        cls,
        candidate,
        candidate_rec,
        candidate_coefficients,
        kcandidate,
        rhs_effective_part,
        effective_part_coeffs,
        k: Union[Number, int, Symbol],
    ):
        equations = cls.__construct_equations__(
            candidate_rec,
            candidate_coefficients,
            kcandidate,
            rhs_effective_part,
            effective_part_coeffs,
            k,
        )
        equations = [sympify(e) for e in equations]
        symbols = list(candidate_coefficients) + list(effective_part_coeffs)
        if isinstance(k, Symbol):
            symbols.append(k)
        symbols = [sympify(s) for s in symbols]
        if isinstance(k, Symbol):
            solutions = nonlinsolve(equations, symbols)
        else:
            solutions = linsolve(equations, symbols)
        solutions = [{sym: val for sym, val in zip(symbols, sol)} for sol in solutions]
        non_trivial_solutions = [
            sol for sol in solutions if candidate.xreplace(sol) != 0
        ]

        return non_trivial_solutions

    @classmethod
    def get_invariants(
        cls,
        candidate,
        rec_builder,
        solutions,
        rhs_effective_part,
        effective_part_coeffs,
        numeric_roots,
        numeric_croots,
        numeric_eps,
        program,
        k: Union[Number, int, Symbol],
    ):
        if len(solutions) == 0:
            return None
        effective_part_solution = cls.__solve_effective_part__(
            rhs_effective_part,
            effective_part_coeffs,
            numeric_roots,
            numeric_croots,
            numeric_eps,
            program,
        )
        invariants = []
        initial_candidate = cls.__get_init_value_candidate__(candidate, rec_builder)
        for solution in solutions:
            k = k.xreplace(solution) if isinstance(k, Symbol) else k
            ans = solve_rec_by_summing(
                rec_coeff=k,
                init_value=initial_candidate.xreplace(solution),
                inhom_part=sympify(effective_part_solution).xreplace(solution),
            )
            invariants.append((candidate.xreplace(solution), ans))
        return invariants

    @classmethod
    def synth_inv(
        cls,
        candidate_vars,
        inv_deg,
        program: Program,
        numeric_roots,
        numeric_croots,
        numeric_eps,
        k: Union[Number, int, None] = None,
    ):
        rec_builder = RecBuilder(program)
        candidate, candidate_rec, candidate_coefficients = cls.construct_candidate(
            candidate_vars, inv_deg, program
        )
        rhs_effective_part, effective_part_coeffs = cls.construct_inhomogeneous_part(
            candidate_rec, program.defective_variables, program.variables
        )
        k, kcandidate = cls.construct_homogenous_part(candidate, k)
        solutions = cls.solve_quadratic_system(
            candidate,
            candidate_rec,
            candidate_coefficients,
            kcandidate,
            rhs_effective_part,
            effective_part_coeffs,
            k,
        )
        return cls.get_invariants(
            candidate,
            rec_builder,
            solutions,
            rhs_effective_part,
            effective_part_coeffs,
            numeric_roots,
            numeric_croots,
            numeric_eps,
            program,
            k,
        )
