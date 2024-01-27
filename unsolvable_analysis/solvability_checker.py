from typing import Set, Tuple

from symengine.lib.symengine_wrapper import Symbol
from program import Program
from program.assignment import PolyAssignment
from utils import expressions, Graph


effective_vars = Set[Symbol]
defective_vars = Set[Symbol]


class SolvabilityChecker:
    """
    Constructs the variable dependency graph and returns the set of effective and defective variables.
    """

    @classmethod
    def _is_simple(cls, v, program: Program):
        return (
            v in program.finite_variables
            or v in program.dist_variables
            or v in program.func_variables
        )

    @classmethod
    def _get_infinite_var_power(cls, powers, program):
        index_to_vars = {i: var for i, var in enumerate(program.variables)}
        for i in range(len(powers)):
            if powers[i] > 0 and not cls._is_simple(index_to_vars[i], program):
                return powers[i]
        return 0

    @classmethod
    def _get_dependency_graph(cls, program: Program):
        index_to_vars = {i: var for i, var in enumerate(program.variables)}
        dependency_graph = Graph(len(program.variables))
        for assign in program.loop_body:
            dependency_graph.add_node(assign.variable)
        for assign in program.loop_body:
            if isinstance(assign, PolyAssignment):
                for poly in assign.polynomials:
                    monoms, const = expressions.get_terms_with_vars(
                        poly.expand(), program.variables
                    )
                    for powers, coeff in monoms:
                        infinite_vars_cnt = sum(
                            [
                                (
                                    1
                                    if powers[i] > 0
                                    and not cls._is_simple(index_to_vars[i], program)
                                    else 0
                                )
                                for i in range(len(powers))
                            ]
                        )
                        infinite_var_pw = cls._get_infinite_var_power(powers, program)
                        if infinite_vars_cnt <= 1:
                            for i in range(len(powers)):
                                if powers[i] > 0:
                                    rhs_var = index_to_vars[i]
                                    if infinite_var_pw == 1 or infinite_vars_cnt == 0:
                                        dependency_graph.add_edge(
                                            assign.variable, rhs_var, 1
                                        )
                                    else:
                                        dependency_graph.add_edge(
                                            assign.variable, rhs_var, 2
                                        )
                        else:
                            for i in range(len(powers)):
                                if powers[i] > 0:
                                    rhs_var = index_to_vars[i]
                                    dependency_graph.add_edge(
                                        assign.variable, rhs_var, 2
                                    )
        return dependency_graph

    @classmethod
    def get_variables(cls, program: Program) -> Tuple[effective_vars, defective_vars]:
        dependency_graph = SolvabilityChecker._get_dependency_graph(program)
        defective_vars = dependency_graph.get_defective_nodes()
        effective_vars = set(program.variables) - set(defective_vars)
        return set(effective_vars), set(defective_vars)
