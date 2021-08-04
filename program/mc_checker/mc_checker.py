from typing import Set, Tuple
from symengine.lib.symengine_wrapper import Symbol
from program import Program
from program.assignment import PolyAssignment
from program.assignment import DistAssignment
from utils import graph

GoodVars = Set[Symbol]
BadVars = Set[Symbol]


class MCChecker:
    @classmethod
    def get_term_vars(cls, term):
        for i in range(len(term) - 1):
            if term[i] == "*" and term[i + 1] == "*":
                term = term[:i] + "^^" + term[i + 2:]
        m = term.split("*")

        result = []  # eliminate constant numbers and symbolic variables
        for item in m:
            if '0' <= item[0] <= '9':
                continue
            result.append(item)
        # TODO remove symbolic variables from result
        return result

    @classmethod
    def clean_var(cls, x):  # remove power and negative sign
        if "^^" in x:
            x = x[:x.find("^^")]
        if x[0] == '-':
            x = x[1:]
        return x

    @classmethod
    def get_mc_variables(cls, program: Program) -> Tuple[GoodVars, BadVars]:
        # TODO implement
        dependency_graph = graph.Graph()
        for assign in program.loop_body:
            print("Adding node {}".format(str(assign.variable)))
            dependency_graph.add_node(str(assign.variable))

        print("##########ASSIGNMENTS:############")
        for assign in program.loop_body:
            if isinstance(assign, PolyAssignment):
                print("Current assignment: {}".format(assign))
                print()

                assign_var = str(assign.variable)
                for poly in assign.polynomials:
                    print("Terms of polynomial {} are {}".format(poly, poly.args))
                    for term in poly.args:
                        term_vars = MCChecker.get_term_vars(str(term))
                        print("Term {} splits into {}".format(term, term_vars))

                        if len(term_vars) == 1:
                            d_var = MCChecker.clean_var(term_vars[0])
                            if "^^" in term_vars[0]:
                                dependency_graph.add_edge(assign_var, d_var, 2)  # non-linear dependency
                            else:
                                dependency_graph.add_edge(assign_var, d_var, 1)  # linear dependency
                        else:
                            for v in term_vars:
                                d_var = MCChecker.clean_var(v)
                                dependency_graph.add_edge(assign_var, d_var, 2)

                    print()

                print()
                print()
            elif isinstance(assign, DistAssignment):
                print("DIST")

        return set(), set()
