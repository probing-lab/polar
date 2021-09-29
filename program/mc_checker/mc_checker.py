from typing import Set, Tuple

from symengine.lib.symengine_wrapper import Symbol
from program import Program
from program.assignment import PolyAssignment, DistAssignment
from utils import expressions, Graph


GoodVars = Set[Symbol]
BadVars = Set[Symbol]


class MCChecker:
    """
    Class which constructs the dependency graph between the variables assigned and
    returns the set of moment computable and non moment computable variables later used for
    finding moment computable combinations.
    """

    @classmethod
    def __is_simple__(cls, v, program: Program):
        return v in program.finite_variables or v in program.dist_variables

    @classmethod
    def __get_infinite_var_power__(cls, powers, program):
        index_to_vars = {i: var for i, var in enumerate(program.variables)}
        for i in range(len(powers)):
            if powers[i] > 0 and not cls.__is_simple__(index_to_vars[i], program):
                return powers[i]
        return 0

    @classmethod
    def __get_dependency_graph__(cls, program: Program):
        index_to_vars = {i: var for i, var in enumerate(program.variables)}
        dependency_graph = Graph(len(program.variables))
        for assign in program.loop_body:
            dependency_graph.add_node(assign.variable)
        for assign in program.loop_body:
            if isinstance(assign, PolyAssignment):
                for poly in assign.polynomials:
                    monoms, const = expressions.get_terms_with_vars(poly.expand(), program.variables)
                    for powers, coeff in monoms:
                        infinite_vars_cnt = sum(
                            [1 if powers[i] > 0 and not cls.__is_simple__(index_to_vars[i], program) else 0
                             for i in range(len(powers))]
                        )
                        infinite_var_pw = cls.__get_infinite_var_power__(powers, program)
                        if infinite_vars_cnt <= 1:
                            for i in range(len(powers)):
                                if powers[i] > 0:
                                    rhs_var = index_to_vars[i]
                                    if infinite_var_pw == 1 or infinite_vars_cnt == 0:
                                        dependency_graph.add_edge(assign.variable, rhs_var, 1)
                                    else:
                                        dependency_graph.add_edge(assign.variable, rhs_var, 2)
                        else:
                            for i in range(len(powers)):
                                if powers[i] > 0:
                                    rhs_var = index_to_vars[i]
                                    dependency_graph.add_edge(assign.variable, rhs_var, 2)
        return dependency_graph

    @classmethod
    def get_mc_variables(cls, program: Program) -> Tuple[GoodVars, BadVars]:
        dependency_graph = MCChecker.__get_dependency_graph__(program)
        bad_variables = dependency_graph.get_bad_nodes()
        good_variables = set(program.variables) - set(bad_variables)
        return set(good_variables), set(bad_variables)
