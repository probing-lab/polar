from utils import get_unique_var
from symengine.lib.symengine_wrapper import Symbol
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