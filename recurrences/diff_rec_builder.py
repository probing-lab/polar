from functools import lru_cache
from typing import Dict, Set, List, Tuple
from symengine.lib.symengine_wrapper import Derivative, Expr, Symbol, Function, sympify, One, Zero
from program import Program
from program.sensitivity.sensitivity_analyzer import SensivitiyAnalyzer, SymbolSet
from recurrences.rec_builder import RecBuilder
from utils.strings import random_string
from .recurrences import Recurrences
from utils import get_terms_with_var, get_terms_with_vars, get_monoms


class DiffRecBuilder:
    """
    Class providing the construction of recurrences of differentiated monomials for a given program.
    """

    program: Program

    def __init__(self, program: Program, param: Symbol):
        self.program = program
        self.param = param
        self.rec_builder = RecBuilder(program)

        self.var2fun_dict = {}
        self.fun2var_dict = {}
        self.diff2var_dict = {}

        self.dep_vars, _ = SensivitiyAnalyzer.get_dependent_variables(program, param)
        for var in self.dep_vars:
            fun = Function(var.name)(self.param)
            self.var2fun_dict[var] = fun
            self.fun2var_dict[fun] = var

            diff_var = sympify('diff_' + var.name + '_' + random_string(4)) # use random postfix for diff_variable to avoid collisions
            diff_fun = fun.diff(self.param)
            self.diff2var_dict[diff_fun] = diff_var

    def __differentiate_goal__(self, goal: Expr) -> List[Expr]:
        # replace p-dependent variables x with functions x(param), so symengine diff works properly
        goal = sympify(goal).xreplace(self.var2fun_dict)

        # goal might become a polynomial by differentiating
        return goal.diff(self.param).expand()

    @lru_cache(maxsize=None)
    def get_recurrences(self, monomial: Expr) -> Tuple[Recurrences, List[Expr]]:
        diff_poly = self.__differentiate_goal__(monomial)
        diff_monomials = diff_poly.args if diff_poly.is_Add else [diff_poly]
        to_process = set(diff_monomials)

        # iteratively get recurrences for monoms and then check if more monomials are needed
        #   to solve the recurrence
        processed = set()
        recurrence_dict_fun = {}
        while to_process:
            next_monom = to_process.pop()
            rec = self.get_recurrence(next_monom)
            recurrence_dict_fun[next_monom] = rec
            processed.add(next_monom)
            monoms = self.__get_monoms_incl_fun__(rec, constant_symbols=self.program.symbols)
            for _, monom in monoms:
                if monom not in processed:
                    to_process.add(monom)

        init_values_dict_fun = self.get_initial_values(processed)

        # for the solver, map all parameter dependent functions back to the variables and
        #   replace all the derivatives with shorthand notations
        recurrence_dict_var = {}
        init_values_dict_var = {}
        for key in recurrence_dict_fun:
            varkey = key.xreplace(self.diff2var_dict).xreplace(self.fun2var_dict)
            recurrence_dict_var[varkey] = recurrence_dict_fun[key].xreplace(self.diff2var_dict).xreplace(self.fun2var_dict)
            init_values_dict_var[varkey] = init_values_dict_fun[key].xreplace(self.diff2var_dict).xreplace(self.fun2var_dict)

        return Recurrences(recurrence_dict_var, init_values_dict_var, self.program)

    @lru_cache(maxsize=None)
    def get_recurrence(self, monomial: Expr):
        """
        Get recurrence for monomials using derivatives and p-dependent variables/functions
        """
        factors = monomial.args if monomial.is_Mul else [monomial]

        result = One()
        variable_part = One()
        for factor in factors:
            if isinstance(factor, Derivative):
                function, _ = factor.args
                # standard solver doesn't know about x(param), only x
                variable = self.fun2var_dict[function]
                # translate back variable to function
                variable_rec = self.rec_builder.get_recurrence(variable).xreplace(self.var2fun_dict)
                result = result * variable_rec.diff(self.param)
            else:
                variable_part = variable_part * factor

        if variable_part.is_Number:
            variable_rec = variable_part
        else:
            # translate functions to variables
            variable_part = variable_part.xreplace(self.fun2var_dict)
            # get recurrence and translate to function world
            variable_rec = self.rec_builder.get_recurrence(variable_part).xreplace(self.var2fun_dict)

        return (result * variable_rec).simplify().expand()

    def __get_monoms_incl_fun__(self, poly: Expr, constant_symbols: SymbolSet):
        """
        Specialized version of get_monoms, to also take care of functions/derivatives
        """
        monoms = []
        constant = Zero()
        terms = poly.args if poly.is_Add else [poly]
        for term in terms:
            free_symbols_function = term.free_symbols.union(term.atoms(Function)).union(term.atoms(Derivative))
            if not free_symbols_function.difference(constant_symbols):
                constant += term
                continue

            coeff = One()
            monom = One()
            parts = term.args if term.is_Mul else [term]
            for part in parts:
                free_symbols_function = part.free_symbols.union(part.atoms(Function)).union(part.atoms(Derivative))
                if free_symbols_function.difference(constant_symbols):
                    monom *= part
                else:
                    coeff *= part
            monoms.append((coeff, monom))

        return monoms

    def get_initial_values(self, monomials: Set[Expr]):
        result = {}
        for monom in monomials:
            result[monom] = self.get_initial_value(monom)
        return result

    def get_initial_value(self, monomial: Expr):
        """
        Get initial values for monomial, variable initial values are delegated to the standard rec_builder,
        differential initial values are obtained by differentiating the initial value of the variables.
        """
        factors = monomial.args if monomial.is_Mul else [monomial]

        result = One()
        variable_part = One()
        for factor in factors:
            if isinstance(factor, Derivative):
                function, _ = factor.args
                # standard solver doesn't know about x(param), only x
                variable = self.fun2var_dict[function]
                # translate back variable to function
                variable_ini = self.rec_builder.get_initial_value(variable).xreplace(self.var2fun_dict)
                result = result * variable_ini.diff(self.param)
            else:
                variable_part = variable_part * factor

        if variable_part.is_Number:
            variable_rec = variable_part
        else:
            # translate functions to variables
            variable_part = variable_part.xreplace(self.fun2var_dict)
            # get recurrence and translate to function world
            variable_rec = self.rec_builder.get_initial_value(variable_part).xreplace(self.var2fun_dict)

        return (result * variable_rec).simplify().expand()

    def is_solvable(self, monom: Expr, program: Program):
        defective_vars = program.non_mc_variables
        diffdef, _ = SensivitiyAnalyzer.get_diff_defective_variables(self.program, self.dep_vars, self.param)

        diff_poly = self.__differentiate_goal__(monom)

        # cannot compute moment goal if term contains defective variables or derivatives of diff-defective ones
        terms = diff_poly.args if diff_poly.is_Add else [diff_poly]
        for term in terms:
            parts = term.args if term.is_Mul else [term]
            for part in parts:
                if isinstance(part, Derivative):
                    fun, _ = part.args
                    if self.fun2var_dict[fun] in diffdef:
                        return False
                elif isinstance(part, Function):
                    if self.fun2var_dict[fun] in defective_vars:
                        return False
                elif part in defective_vars:
                    return False
        return True

    def get_solution(self, monom: Expr, solvers):
        diff_poly = self.__differentiate_goal__(monom)
        diff_monom_terms = diff_poly.args if diff_poly.is_Add else [diff_poly]

        result = Zero()
        is_exact = True
        for term in diff_monom_terms:
            term = term.xreplace(self.diff2var_dict).xreplace(self.fun2var_dict) # map Derivatives to diff_* variables
            solver = solvers[term]
            is_exact = is_exact and solver.is_exact
            result += solvers[term].get(term)
        return sympify(result.simplify()), is_exact
