# from symengine import Eq

from utils import get_unique_var
from symengine.lib.symengine_wrapper import Symbol, solve
from utils import expressions


class MCCombFinder:

    @classmethod
    def get_idx_var(cls, v, vars_to_index):
        return vars_to_index[v]

    @classmethod
    def get_var_idx(cls, i, vars_to_index):
        for var in vars_to_index.keys():
            if vars_to_index[var] == i:
                return var

    @classmethod
    def __get_candidate_terms(cls, pos, vars, deg, pw, s):
        if pos == len(vars):
            if s == 0:  # constant
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
                expr, c = MCCombFinder.__get_candidate_terms(pos + 1, vars, deg, pw, s + i)
                if expr == 0:
                    continue
                ans += expr
                for elem in c:
                    coefficients.add(elem)
        return ans, coefficients,

    @classmethod
    def get_candidate(cls, vars, deg):
        ans, coeffs = MCCombFinder.__get_candidate_terms(0, vars, deg, [0] * len(vars), 0)
        return ans, coeffs

    @classmethod
    def get_good_set(cls, candidate_rec, bad_variables, variables):
        result = set()
        monoms = expressions.get_terms_with_vars(candidate_rec, variables)
        monoms = monoms[0]

        vars_to_index = {var: i for i, var in enumerate(variables)}
        # print(vars_to_index)
        # print(f"monoms of candidate_rec are {monoms}")
        for monom, coeff in monoms:
            bad = False
            term = 0
            for i in range(len(monom)):
                if monom[i] == 0:
                    continue
                cur_var = MCCombFinder.get_var_idx(i, vars_to_index)
                if cur_var in bad_variables:
                    # print(f"{monom} has the bad variable {cur_var}")
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

        print(f"program.variables: {program_variables}")

        print(f"good_coeffs: {good_coeffs}")
        print(f"candidate_coeffs: {candidate_coefficients}")

        k = Symbol('k')
        candidate = (k * candidate).expand()
        print()
        print(f"variables of equation: {list(candidate_coefficients) + [k] + list(good_coeffs)}")
        print(f"candidate_rec_n-1 - k.candidate_n-1 - good = {candidate_rec - candidate - rhs_good_part}")
        print()

        equation_terms = {}
        candidate_rec_monoms = expressions.get_monoms(candidate_rec, candidate_coefficients, with_constant=True)
        kcandidate_monoms = expressions.get_monoms(candidate, candidate_coefficients | {k}, with_constant=True)
        good_part_monoms = expressions.get_monoms(rhs_good_part, good_coeffs, with_constant=True)

        print()
        print(f"candidate_rec_monoms = {candidate_rec_monoms}")
        print()
        print(f"kcandidate_monoms = {kcandidate_monoms}")
        print()
        print(f"good_part_monoms = {good_part_monoms}")

        for coeff, monom in candidate_rec_monoms:
            equation_terms[monom] = equation_terms.get(monom, 0) + coeff
        for coeff, monom in kcandidate_monoms:
            equation_terms[monom] = equation_terms.get(monom, 0) - coeff
        for coeff, monom in good_part_monoms:
            equation_terms[monom] = equation_terms.get(monom, 0) - coeff

        print(f"equation_terms: {equation_terms}")


        equations = []
        for eq in equation_terms.values():
            equations.append(eq)

        print(f"equations = {equations}")
        sol = solve(equations, list(candidate_coefficients) + [k] + list(good_coeffs))
        print(f"sol = {sol}")
