from typing import Set, Tuple

from symengine.lib.symengine_wrapper import Symbol
from program import Program
from program.assignment import PolyAssignment
from program.assignment import DistAssignment
from utils import graph
from utils import expressions


GoodVars = Set[Symbol]
BadVars = Set[Symbol]


class MCChecker:

    @classmethod
    def get_mc_variables(cls, program: Program) -> Tuple[GoodVars, BadVars]:
        # TODO implement

        print("##########PROGRAM VARIABLES##########")
        print(program.variables)
        vars_to_index = {var: i for i, var in enumerate(program.variables)}
        print(vars_to_index)

        dependency_graph = graph.Graph()
        for assign in program.loop_body:
            print("Adding node {}".format(str(assign.variable)))
            dependency_graph.add_node(str(assign.variable))
        print()

        print("##########ASSIGNMENTS:############")
        for assign in program.loop_body:
            if isinstance(assign, PolyAssignment):
                print("Current assignment: {}".format(assign))
                assign_var = str(assign.variable)
                for poly in assign.polynomials:
                    # TODO: handle dependencies in assignments including if-statements
                    monoms = expressions.get_terms_with_vars(poly, program.variables)
                    print("Poly: {} , Monomials: {}".format(poly, monoms))

            elif isinstance(assign, DistAssignment):
                print("Current assignment: {}".format(assign))

            print()

        return set(), set()
