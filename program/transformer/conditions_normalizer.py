from typing import List

from .transformer import Transformer
from program import Program
from ..assignment import Assignment


class ConditionsNormalizer(Transformer):
    """
    Bla
    """
    program: Program

    def execute(self, program: Program) -> Program:
        self.program = program
        self.__normalize_conditions__(self.program.initial)
        self.__normalize_conditions__(self.program.loop_body)
        return program

    def __normalize_conditions__(self, assignments: List[Assignment]):
        for assign in assignments:
            assign.condition = assign.condition.get_normalized(self.program)
