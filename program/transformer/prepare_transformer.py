from typing import List
from .transformer import Transformer
from program import Program
from program.assignment import Assignment


class PrepareTransformer(Transformer):
    """
    Prepares some final data about the program. So it can be better processed afterwards.
    The transformer requires that the passed program is already flattened, meaning does not contain any if-statements.
    """
    program: Program

    def execute(self, program: Program) -> Program:
        self.program = program
        program.initial = self.__prepare_assignments__(program.initial)
        program.loop_body = self.__prepare_assignments__(program.loop_body)
        program.variables = program.initial.keys() | program.loop_body.keys()
        return program

    def __prepare_assignments__(self, assignments: List[Assignment]):
        new_assignments = {}
        for assign in assignments:
            new_assignments[assign.variable] = assign
        return new_assignments
