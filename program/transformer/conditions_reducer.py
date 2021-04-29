from typing import List
from .transformer import Transformer
from program import Program
from program.assignment import Assignment, PolyAssignment


class ConditionsReducer(Transformer):
    """
    Transforms all condition atoms in the program to the form: <variable> <comparison> <integer>
    """
    program: Program

    def execute(self, program: Program) -> Program:
        self.program = program
        self.program.initial = self.__reduce_conditions__(self.program.initial)
        self.program.loop_body = self.__reduce_conditions__(self.program.loop_body)
        return program

    def __reduce_conditions__(self, assignments: List[Assignment]):
        new_assignments = []
        for assign in assignments:
            aliases = assign.condition.reduce()
            for new_var, expression in aliases:
                new_assignments.append(PolyAssignment.deterministic(new_var, expression.simplify()))
            new_assignments.append(assign)

        return new_assignments
