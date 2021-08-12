from utils import get_unique_var
from symengine.lib.symengine_wrapper import Symbol, solve
from sympy import linsolve, sympify
from utils import expressions


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
    def get_candidate(cls, vars, deg):
        ans, coeffs = cls.__get_candidate_terms__(0, vars, deg, [0] * len(vars), 0)
        return ans, coeffs

    @classmethod
    def get_good_set(cls, candidate_rec, bad_variables, variables):
        result = set()
        monoms = expressions.get_terms_with_vars(candidate_rec, variables)[0]
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
    def get_good_poly(cls, good_set):
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
    def find_good_combination(cls, candidate, candidate_rec, good_set, candidate_coefficients, program_variables):
        rhs_good_part, good_coeffs = MCCombFinder.get_good_poly(good_set)
        k = Symbol(get_unique_var("k"))
        candidate = (k * candidate).expand()

        equation_terms = {}
        candidate_rec_monoms = expressions.get_monoms(candidate_rec, candidate_coefficients, with_constant=True)
        kcandidate_monoms = expressions.get_monoms(candidate, candidate_coefficients | {k}, with_constant=True)
        good_part_monoms = expressions.get_monoms(rhs_good_part, good_coeffs, with_constant=True)

        for coeff, monom in candidate_rec_monoms:
            equation_terms[monom] = equation_terms.get(monom, 0) + coeff
        for coeff, monom in kcandidate_monoms:
            equation_terms[monom] = equation_terms.get(monom, 0) - coeff
        for coeff, monom in good_part_monoms:
            equation_terms[monom] = equation_terms.get(monom, 0) - coeff

        equations = []
        k_equation = None
        for eq in equation_terms.values():
            if k in eq.free_symbols:
                k_equation = eq
            equations.append(eq)

        print(f"equations = {equations}")
        k_solution = solve(k_equation, k)
        # k_solution = solve(equations, k)
        if len(k_solution.args) != 1:
            # TODO: there is no solution
            pass
        k_value = k_solution.args[0]
        print(f"k_value = {k_value}")
        # if not k_value.is_Number:
            # TODO: should not happen but still handle
        #    pass

        equations = [sympify(eq.xreplace({k: k_value}).expand()) for eq in equations]
        unknowns = [sympify(u) for u in (candidate_coefficients | good_coeffs)]
        print("hiiiiii")
        solutions = linsolve(equations, unknowns)
        print(f"byeeee {solutions}")
        return k_value, solutions
