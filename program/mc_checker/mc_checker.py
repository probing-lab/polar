from typing import Set, Tuple

from symengine.lib.symengine_wrapper import Symbol
from program import Program
from program.assignment import PolyAssignment
from utils import expressions, graph


GoodVars = Set[Symbol]
BadVars = Set[Symbol]


class MCChecker:
    """
    Class which constructs the dependency graph between the variables assigned and
    returns the set of moment computable and non moment computable variables later used for
    finding moment computable combinations.
    """

    @classmethod
    def __get_dependency_graph__(cls, program: Program):
        index_to_vars = {i: var for i, var in enumerate(program.variables)}
        dependency_graph = graph.Graph(program)

        for assign in program.loop_body:
            dependency_graph.add_node(assign.variable)
        for assign in program.loop_body:
            if isinstance(assign, PolyAssignment):
                for poly in assign.polynomials:
                    monoms, const = expressions.get_terms_with_vars(poly, program.variables)
                    for powers, coeff in monoms:
                        non_zero_powers = sum([1 for p in powers if p > 0])
                        if non_zero_powers == 1:
                            for i in range(len(powers)):
                                if powers[i] > 0:
                                    rhs_var = index_to_vars[i]
                                    if powers[i] == 1:
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
