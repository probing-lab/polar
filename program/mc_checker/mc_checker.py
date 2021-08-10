from typing import Set, Tuple

from symengine.lib.symengine_wrapper import Symbol
from program import Program
from program.assignment import PolyAssignment
from program.assignment import DistAssignment
from utils import graph, expressions


GoodVars = Set[Symbol]
BadVars = Set[Symbol]


class MCChecker:

    @classmethod
    def get_idx_var(cls, v, vars_to_index):
        return vars_to_index[v]

    @classmethod
    def get_var_idx(cls, i, vars_to_index):
        for var in vars_to_index.keys():
            if vars_to_index[var] == i:
                return var

    @classmethod
    def get_mc_variables(cls, program: Program) -> Tuple[GoodVars, BadVars]:
        # print("##########PROGRAM VARIABLES##########")
        # print(program.variables)
        vars_to_index = {var: i for i, var in enumerate(program.variables)}
        # print(vars_to_index)

        dependency_graph = graph.Graph(program)
        for assign in program.loop_body:
            # print("Adding node {}".format(assign.variable))
            dependency_graph.add_node(assign.variable)
        # print()
        # print("##########FINITE VARIABLES##########")
        # print(program.finite_variables)
        # print()

        # print("##########ASSIGNMENTS:############")
        for assign in program.loop_body:
            if isinstance(assign, PolyAssignment):
                # print("Current assignment: {}".format(assign))
                for poly in assign.polynomials:
                    # TODO: handle dependencies in assignments including if-statements
                    monoms, const = expressions.get_terms_with_vars(poly, program.variables)
                    # print("Poly: {} , Monomials: {}".format(poly, monoms))

                    for powers, coeff in monoms:
                        non_zero_powers = sum([1 for p in powers if p > 0])
                        # print("monom: {} , non_zero_powers: {}".format(powers, non_zero_powers))
                        # print()
                        if non_zero_powers == 1:  # linear dependency
                            for i in range(len(powers)):
                                if powers[i] > 0:
                                    rhs_var = MCChecker.get_var_idx(i, vars_to_index)
                                    if powers[i] == 1:
                                        dependency_graph.add_edge(assign.variable, rhs_var, 1)
                                    else:
                                        dependency_graph.add_edge(assign.variable, rhs_var, 2)

                        else:  # polynomial dependency on all non zero powers
                            for i in range(len(powers)):
                                if powers[i] > 0:
                                    rhs_var = MCChecker.get_var_idx(i, vars_to_index)
                                    dependency_graph.add_edge(assign.variable, rhs_var, 2)


            elif isinstance(assign, DistAssignment):
                pass
                # print("Current assignment: {}".format(assign))

            # print("------------------------")

        # print("Checking for cycles...")
        bad_variables = dependency_graph.get_bad_nodes()
        # print("Bad cycles checked!")

        good_variables = set()
        for v in program.variables:
            if v not in bad_variables:
                good_variables.add(v)

        print("goods: {}".format(good_variables))
        print("bad: {}".format(bad_variables))

        return set(good_variables), set(bad_variables)
