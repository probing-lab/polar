from utils import get_unique_var, solve_rec_by_summing, get_terms_with_vars, get_monoms
from symengine.lib.symengine_wrapper import Symbol
from sympy import solve, sympify
from recurrences import RecBuilder
from program import Program
from recurrences.solver import RecurrenceSolver


class MCCombFinder:
    """
    Checks if a combination of [non-mc] variables called candidate exists s.t it can be written in the form:
    candidate_n = candidate_rec_n-1 = k*candidate_n-1 + good where good is a sum of moment computable terms
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
        return ans, coefficients,

    @classmethod
    def __get_candidate__(cls, vars, deg):
        ans, coeffs = cls.__get_candidate_terms__(0, vars, deg, [0] * len(vars), 0)
        return ans, coeffs

    @classmethod
    def __get_good_set__(cls, candidate_rec, bad_variables, variables):
        result = set()
        monoms = get_terms_with_vars(candidate_rec, variables)[0]
        index_to_vars = {i: var for i, var in enumerate(variables)}
        for monom, coeff in monoms:
            bad = False
            term = 0
            for i in range(len(monom)):
                if monom[i] == 0:
                    continue
                cur_var = index_to_vars[i]
                if cur_var in bad_variables:
                    bad = True
                term += cur_var ** monom[i]
            if not bad and sum(monom) > 0:
                result.add(term)
        return result

    @classmethod
    def __get_good_poly__(cls, good_set):
        rhs_good_part = 0
        symbols = set()
        for term in good_set:
            coeff = Symbol(get_unique_var())
            symbols.add(coeff)
            rhs_good_part = coeff * term

        coeff = Symbol(get_unique_var())
        symbols.add(coeff)
        rhs_good_part += coeff

        return rhs_good_part, symbols

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
        ans = 0
        monoms = get_monoms(candidate, rec_builder.program.variables)
        for monom, coeff in monoms:
            ans += rec_builder.get_initial_value(monom) * coeff
        return ans

    @classmethod
    def __construct_equations__(cls, candidate_rec, candidate_coefficients, kcandidate, rhs_good_part, good_coeffs, k):
        candidate_rec_monoms = get_monoms(candidate_rec, candidate_coefficients, with_constant=True)
        kcandidate_monoms = get_monoms(kcandidate, candidate_coefficients | {k}, with_constant=True)
        good_part_monoms = get_monoms(rhs_good_part, good_coeffs, with_constant=True)
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
        Keeps plugging in solutions of SymPy and solving new-made equations until all evaluate to zero
        """
        nice_solutions = []
        for solution in solutions:
            solution_exact, nequations, nequations_variables = cls.__solution_exact__(equations, solution)
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
                solution_exact, nequations, nequations_variables = cls.__solution_exact__(equations, solution)
            if not wrong_solution:
                nice_solutions.append(solution)
        solutions = nice_solutions
        nice_solutions = []
        for solution in solutions:
            if candidate.xreplace(solution) == 0:
                continue
            if not sympify(k) in solution:
                continue
            if solution[sympify(k)] == 0:
                continue
            nice_solutions.append(solution)
        return nice_solutions

    @classmethod
    def __solve_good_part__(cls, rhs_good_part, good_coeffs, numeric_roots, numeric_croots, numeric_eps, program):
        good_part_monoms = get_monoms(rhs_good_part, good_coeffs, with_constant=True)
        good_part_solution = 0
        for coeff, monom in good_part_monoms:
            if monom == 1:
                good_part_solution += coeff
                continue
            rec_builder = RecBuilder(program)
            recs = rec_builder.get_recurrences(monom)
            rec_solver = RecurrenceSolver(
                recurrences=recs,
                numeric_roots=numeric_roots,
                numeric_croots=numeric_croots,
                numeric_eps=numeric_eps
            )
            good_part_solution += coeff * rec_solver.get(monom)
        good_part_solution = good_part_solution.xreplace({sympify("n"): sympify("n") - 1})
        return good_part_solution


    @classmethod
    def find_good_combination(cls, combination_vars, combination_deg, program: Program,
                              numeric_roots, numeric_croots, numeric_eps):
        candidate, candidate_coefficients = cls.__get_candidate__(combination_vars, combination_deg)
        rec_builder = RecBuilder(program)
        candidate_rec = rec_builder.get_recurrence_poly(candidate, combination_vars)

        good_set = cls.__get_good_set__(candidate_rec, program.non_mc_variables, program.variables)
        rhs_good_part, good_coeffs = cls.__get_good_poly__(good_set)
        k = Symbol(get_unique_var("k"), nonzero=True)
        kcandidate = (k * candidate).expand()

        equations = cls.__construct_equations__(
            candidate_rec, candidate_coefficients, kcandidate, rhs_good_part, good_coeffs, k
        )
        solutions = solve(equations, list(candidate_coefficients) + [k] + list(good_coeffs), dict = True)
        nice_solutions = cls.__get_nice_solutions__(solutions, equations, candidate, k)
        if len(nice_solutions) == 0:
            print(f"No combination found with degree {combination_deg}. Try using other degrees.")
            return

        good_part_solution = cls.__solve_good_part__(
            rhs_good_part, good_coeffs, numeric_roots, numeric_croots, numeric_eps, program
        )

        print(f"candidate = {candidate}")
        print()

        initial_candidate = cls.__get_init_value_candidate__(candidate, rec_builder)
        for solution in nice_solutions:
            ans = solve_rec_by_summing(
                rec_coeff=solution[sympify(k)],
                init_value=initial_candidate,
                inhom_part=sympify(good_part_solution)
            )
            ans = ans.xreplace(solution)
            print(f"E({candidate.xreplace(solution)})[n] = {ans}")
            print()
