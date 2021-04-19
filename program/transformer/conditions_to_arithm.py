from typing import List
from diofant import sympify
from utils import get_unique_var
from .transformer import Transformer
from program import Program
from program.assignment import Assignment, PolyAssignment, DistAssignment
from program.condition import TrueCond


class ConditionsToArithm(Transformer):
    """
    Turns conditions of all assignments into arithmetic:

    x = Assignment | Condition : Default --> x = [Condition]*Assignment + [not Condition]*Default

    The transformer requires that the passed program is flattened, meaning it does not contain any if-statements.
    """
    program: Program

    def execute(self, program: Program) -> Program:
        self.program = program
        program.initial = self.__conditions_to_arithm__(program.initial)
        program.loop_body = self.__conditions_to_arithm__(program.loop_body)
        return program

    def __conditions_to_arithm__(self, assignments: List[Assignment]):
        new_assignments: List[Assignment] = []
        for assign in assignments:
            arithm_cond = assign.condition.to_arithm(self.program)
            if arithm_cond == 1:
                assign.condition = TrueCond()
                new_assignments.append(assign)
                continue

            if isinstance(assign, PolyAssignment):
                assign.poly = arithm_cond * assign.poly + (1 - arithm_cond) * assign.default
                assign.condition = TrueCond()
                new_assignments.append(assign)

            if isinstance(assign, DistAssignment):
                new_var = sympify(get_unique_var())
                dist_assign = DistAssignment(new_var, assign.distribution)
                poly = arithm_cond * new_var + (1 - arithm_cond) * assign.default
                poly_assign = PolyAssignment(assign.variable, poly)
                new_assignments.append(dist_assign)
                new_assignments.append(poly_assign)

        return new_assignments
