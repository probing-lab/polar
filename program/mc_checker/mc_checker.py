from typing import Set, Tuple
from symengine.lib.symengine_wrapper import Symbol
from program import Program


GoodVars = Set[Symbol]
BadVars = Set[Symbol]


class MCChecker:

    @classmethod
    def get_mc_variables(cls, program: Program) -> Tuple[GoodVars, BadVars]:
        # TODO implement
        return set(), set()
