from bdb import effective
from symtable import Symbol
from typing import Set, Tuple
from numpy import isin
from sympy import Poly
from program import Program
from program.mc_checker.mc_checker import MCChecker
from utils import expressions
from symengine.lib.symengine_wrapper import Symbol as SymengineSymbol

from program.assignment.poly_assignment import PolyAssignment

SymbolSet = Set[SymengineSymbol]


class SensivitiyAnalyzer:
    @classmethod
    def __assignment_uses_dependent_variable__(cls, assignment: PolyAssignment, vars: Set[SymengineSymbol]) -> bool:
        """
        Returns true if the assignment makes use of at least one variable in set vars
        """
        assert isinstance(assignment, PolyAssignment)
        for poly in assignment.polynomials:
            if(len(poly.free_symbols.intersection(vars)) != 0):
                return True
        return False

    @classmethod
    def __assignment_uses_parameter__(cls, assignment: PolyAssignment, param: SymengineSymbol) -> bool:
        """
        Returns true if the assignment uses the symbolic parameter param
        """
        assert isinstance(assignment, PolyAssignment)
        for poly in assignment.polynomials:
            if param in poly.free_symbols:
                return True
        return False

    @classmethod
    def get_dependent_variables(cls, program: Program, param: SymengineSymbol) -> Tuple[SymbolSet, SymbolSet]:

        """
        Find all program variables that are (in-)dependent on some symbolic parameter.
        Depdencies include:
            1. initial value contains param
            2. some assignment uses param
            3. some other variable that uses param (transitive)
        """

        assert param in program.symbols
        dependent_vars = set()

        # check first condition (initial values)
        for initial_action in program.initial:
            if isinstance(initial_action, PolyAssignment):
                if cls.__assignment_uses_parameter__(initial_action, param):
                    dependent_vars.add(initial_action.variable)

        # check second conditions (assignment uses parameter)
        for body_action in program.loop_body:
            if isinstance(body_action, PolyAssignment):
                if cls.__assignment_uses_parameter__(body_action, param):
                    dependent_vars.add(body_action.variable)

        # loop as long as variables are added to the dependent variables (third condition)
        # this is necessary to find all transitive dependencies
        while True:
            old_dep_size = len(dependent_vars)

            for initial_action in program.initial:
                if isinstance(initial_action, PolyAssignment):
                    if (initial_action.variable not in dependent_vars
                            and cls.__assignment_uses_dependent_variable__(initial_action, dependent_vars)):
                        dependent_vars.add(initial_action.variable)

            for body_action in program.loop_body:
                if isinstance(body_action, PolyAssignment):
                    if (body_action.variable not in dependent_vars
                            and cls.__assignment_uses_dependent_variable__(body_action, dependent_vars)):
                        dependent_vars.add(body_action.variable)

            if old_dep_size == len(dependent_vars):
                break

        return dependent_vars, program.variables - dependent_vars

    @classmethod
    def get_diff_defective_variables(cls, program: Program, dependent_vars: SymbolSet,
                                     param: SymengineSymbol) -> Tuple[SymbolSet, SymbolSet]:
        """
        Find all diff-effective and diff-defective variables of the program, with respect to some parameter.
        """
        # dependent_vars = cls.get_dependent_variables(program, param)
        dependency_graph = MCChecker.__get_dependency_graph__(program)
        defective_vars = dependency_graph.get_bad_nodes()
        diff_defective_vars = set()

        # find all param-dependent vars that are part of a non-linear loop
        for dependent_var in dependent_vars:
            if dependency_graph.is_variable_in_nonlinear_cycle(dependent_var):
                # add all reachable variables to the defective vars (note that all of them are by def. dependent)
                reachable_variables = dependency_graph.get_reachable_variables(dependent_var)
                diff_defective_vars.update(reachable_variables)

        # get all assignments to defective, dependent variables (independet variables are not considered)
        defective_assignments = filter((lambda action: isinstance(action, PolyAssignment)
                                        and action.variable in defective_vars and action.variable in dependent_vars),
                                       program.loop_body)

        # find all defective variables that have an assignment with a monomial of the form
        #   f(p)*d, where d is some defective variable and f(param) is some param-dependent term
        for assignment in defective_assignments:
            for poly in assignment.polynomials:
                monoms = expressions.get_monoms(poly.expand())
                for _, monom in monoms:
                    free_vars = monom.free_symbols

                    # throw away monomials without defective variables
                    monom_defective_dependencies = defective_vars.intersection(free_vars)
                    if len(monom_defective_dependencies) == 0:
                        continue

                    # throw away monomials without param-dependent variables
                    monom_dependent_dependencies = dependent_vars.intersection(free_vars)
                    if param in free_vars:
                        monom_dependent_dependencies.add(param)

                    if len(monom_dependent_dependencies) == 0:
                        continue

                    # check if param-dependent variables and defective variables have at least 2 distinct entries
                    if len(monom_defective_dependencies.union(monom_dependent_dependencies)) > 1:
                        # add all reachable variables to the defective vars
                        #   (note that all of them are by definition dependent)
                        reachable_variables = dependency_graph.get_reachable_variables(assignment.variable)
                        diff_defective_vars.update(reachable_variables)

        # sanity checks:
        # 1) no p-independet variable can ever be diff-defective
        assert len(diff_defective_vars.difference(dependent_vars)) == 0
        # 2) all diff-defective vars are also defective (no effective var is diff-defective)
        assert len(defective_vars.intersection(diff_defective_vars)) == len(diff_defective_vars)

        return diff_defective_vars, dependent_vars - diff_defective_vars

    @classmethod
    def get_diff_solvable_program(cls, program: Program, dependent_vars: SymbolSet,
                                  diff_defective_vars: SymbolSet, diff_effective_vars: SymbolSet) -> Program:
        """
        Return the diff-solvable program for some symbolic parameter.
        """
        # TODO: find best way to place this function in the processing pipeline

        # set all p-independent variables to zero (in initial part, remove all other assignments)

        # throw away all defective variables
        # add differentiated variables and recurrences for all remaining, p-dependent variables
        # return new program and run analysis there
        return
