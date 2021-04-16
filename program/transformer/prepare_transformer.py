from typing import List, Dict

from diofant import Symbol

from .transformer import Transformer
from program import Program
from program.assignment import Assignment, PolyAssignment


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
        self.__make_assigns_poly__(program.initial)
        self.__make_assigns_poly__(program.loop_body)
        return program

    def __prepare_assignments__(self, assignments: List[Assignment]):
        new_assignments = {}
        for assign in assignments:
            new_assignments[assign.variable] = assign
        return new_assignments

    def __make_assigns_poly__(self, assignments: Dict[Symbol, Assignment]):
        for _, assign in assignments.items():
            if isinstance(assign, PolyAssignment):
                assign.poly = assign.poly.as_poly(*self.program.variables)
