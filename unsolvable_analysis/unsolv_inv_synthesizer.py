from typing import Union
from utils import get_unique_var, solve_rec_by_summing, get_terms_with_vars, get_monoms
from symengine.lib.symengine_wrapper import Symbol
from sympy import solve, sympify, groebner, Number, linsolve
from recurrences import RecBuilder
from program import Program
from recurrences.solver import RecurrenceSolver


class UnsolvInvSynthesizer:
    """
    Generates all possible polynomial invariants with some given variables upto a fixed degree
    TODO: Some parts this class are not so nice because sympy's solver for polynomial systems of equation is incomplete.
    TODO: Especially finding a combination for a fixed k is not ideal.
    TODO: Fix this as soon as sympy improves their procedure for systems of polynomial equations.
    In essence the class follows the procedure described in our paper
    "Solving Invariant Generation for Unsolvable Loops".
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
    def __solution_exact__(cls, equations, solution):
        nequations = []
        nequations_variables = set()
        okay = True
        for eq in equations:
            substituted_equation = eq.subs(solution).simplify()
            if not substituted_equation.is_number:
                okay = False
                nequations.append(substituted_equation)
                for symb in substituted_equation.free_symbols:
                    nequations_variables.add(symb)
        return okay, nequations, nequations_variables

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
    def __get_nice_solutions__(cls, solutions, equations, candidate, k):
        """
        Keeps plugging in solutions of SymPy and solving new-made equations until all evaluate to zero. Also,
        eliminates trivial solutions.
        """
        nice_solutions = []
        for solution in solutions:
            solution_exact, nequations, nequations_variables = cls.__solution_exact__(
                equations, solution
            )
            wrong_solution = False
            while not solution_exact:
                nsolutions = solve(nequations, nequations_variables)
                if type(nsolutions) is list:
                    if len(nsolutions) == 0:
                        wrong_solution = True
                        break
                else:
                    for var in solution.keys():
                        solution[var] = solution[var].subs(nsolutions).simplify()
                    for var in nsolutions:
                        solution[var] = nsolutions[var]
                (
                    solution_exact,
                    nequations,
                    nequations_variables,
                ) = cls.__solution_exact__(equations, solution)
            if not wrong_solution:
                nice_solutions.append(solution)
        solutions = nice_solutions
        nice_solutions = []
        for solution in solutions:
            if candidate.xreplace(solution) == 0:
                continue
            if not sympify(k) in solution:
                continue
            nice_solutions.append(solution)
        return nice_solutions

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
    def construct_candidate(cls, candidate_vars, combination_deg, program):
        candidate, candidate_coefficients = cls.__get_candidate__(
            candidate_vars, combination_deg
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
    def construct_homogenous_part(cls, candidate):
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
        k,
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
        symbols = list(candidate_coefficients) + list(effective_part_coeffs) + [k]
        symbols = [sympify(s) for s in symbols]
        basis = groebner(equations, *symbols)
        solution_exists = False
        for b in basis:
            if not b.is_symbol:
                solution_exists = True
        if solution_exists:
            print("I found a solution. Maybe I won't tell you.")
        else:
            print("There really really is not solution.")
        solutions = solve([b for b in basis], symbols, dict=True)
        nice_solutions = cls.__get_nice_solutions__(solutions, equations, candidate, k)
        return nice_solutions

    @classmethod
    def get_invariants(
        cls,
        candidate,
        rec_builder,
        nice_solutions,
        rhs_effective_part,
        effective_part_coeffs,
        numeric_roots,
        numeric_croots,
        numeric_eps,
        program,
        k,
    ):
        if len(nice_solutions) == 0:
            return None
        good_part_solution = cls.__solve_effective_part__(
            rhs_effective_part,
            effective_part_coeffs,
            numeric_roots,
            numeric_croots,
            numeric_eps,
            program,
        )
        invariants = []
        initial_candidate = cls.__get_init_value_candidate__(candidate, rec_builder)
        for solution in nice_solutions:
            ans = solve_rec_by_summing(
                rec_coeff=k.xreplace(solution),
                init_value=initial_candidate.xreplace(solution),
                inhom_part=sympify(good_part_solution).xreplace(solution),
            )
            invariants.append((candidate.xreplace(solution), ans))
        return invariants

    @classmethod
    def synth_inv_for_k(
        cls,
        k: Union[Number, int],
        combination_vars,
        combination_deg,
        program: Program,
        numeric_roots,
        numeric_croots,
        numeric_eps,
    ):
        candidate, candidate_coefficients = cls.__get_candidate__(
            combination_vars, combination_deg
        )
        rec_builder = RecBuilder(program)
        candidate_rec = rec_builder.get_recurrence_poly(candidate, combination_vars)

        effective_monoms = cls.__get_effective_monoms__(
            candidate_rec, program.non_mc_variables, program.variables
        )
        rhs_effective_part, effective_part_coeffs = cls.__get_effective_poly__(
            effective_monoms
        )
        kcandidate = (k * candidate).expand()

        equations = cls.__construct_equations__(
            candidate_rec,
            candidate_coefficients,
            kcandidate,
            rhs_effective_part,
            effective_part_coeffs,
            k,
        )

        symbols = list(candidate_coefficients) + list(effective_part_coeffs)
        equations = [sympify(e) for e in equations]
        symbols = [sympify(s) for s in symbols]
        tmp_solutions = linsolve(equations, symbols)
        solutions = []
        for tmps in tmp_solutions:
            if not all([v == 0 for v in tmps]):
                solutions.append(
                    {symbol: value for symbol, value in zip(symbols, tmps)}
                )
        if len(solutions) == 0:
            return None

        effective_part_solutions = cls.__solve_effective_part__(
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
            ans = solve_rec_by_summing(
                rec_coeff=k,
                init_value=initial_candidate.xreplace(solution),
                inhom_part=sympify(effective_part_solutions).xreplace(solution),
            )
            invariants.append((candidate.xreplace(solution), ans))
        return invariants

    @classmethod
    def synth_inv(
        cls,
        combination_vars,
        combination_deg,
        program: Program,
        numeric_roots,
        numeric_croots,
        numeric_eps,
    ):
        rec_builder = RecBuilder(program)
        candidate, candidate_rec, candidate_coefficients = cls.construct_candidate(
            combination_vars, combination_deg, program
        )
        rhs_effective_part, effective_part_coeffs = cls.construct_inhomogeneous_part(
            candidate_rec, program.non_mc_variables, program.variables
        )
        k, kcandidate = cls.construct_homogenous_part(candidate)
        nice_solutions = cls.solve_quadratic_system(
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
            nice_solutions,
            rhs_effective_part,
            effective_part_coeffs,
            numeric_roots,
            numeric_croots,
            numeric_eps,
            program,
            k,
        )
