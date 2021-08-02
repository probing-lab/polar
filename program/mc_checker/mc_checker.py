from typing import Set, Tuple
from symengine.lib.symengine_wrapper import Symbol
from program import Program
from program.assignment import PolyAssignment
from program.assignment import DistAssignment
from sympy import Add

GoodVars = Set[Symbol]
BadVars = Set[Symbol]


class MCChecker:

    @classmethod
    def get_mc_variables(cls, program: Program) -> Tuple[GoodVars, BadVars]:
        # TODO implement

        print("##########ASSIGNMENTS:############")
        for assign in program.loop_body:
            if (isinstance(assign, PolyAssignment)):
                print("Current assignment: {}".format(assign))
                for poly in assign.polynomials:
                    print("Terms of poly {} are {}".format(poly, poly.args))

                print()
            elif (isinstance(assign, DistAssignment)):
                print("DIST")

        return set(), set()