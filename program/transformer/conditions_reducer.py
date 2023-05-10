from typing import List, Dict

from symengine.lib.symengine_wrapper import Symbol

from .transformer import Transformer
from program import Program
from program.assignment import Assignment, PolyAssignment
from program.condition import Atom


class ConditionsReducer(Transformer):
    """
    Transforms all condition atoms in the program to the form: <variable> <comparison> 0
    The transformer requires that the passed program is flattened, meaning it does not contain any if-statements.
    """

    program: Program

    def execute(self, program: Program) -> Program:
        self.program = program
        self.program.initial = self.__reduce_conditions__(self.program.initial)
        self.program.loop_body = self.__reduce_conditions__(self.program.loop_body)
        return program

    def __reduce_conditions__(self, assignments: List[Assignment]):
        new_assignments = []
        store: Dict[Atom, Symbol] = {}
        for assign in assignments:
            aliases = assign.condition.reduce(store)
            for new_var, expression in aliases:
                new_assignments.append(
                    PolyAssignment.deterministic(new_var, expression.simplify())
                )
            new_assignments.append(assign)
            store = {
                k: v
                for k, v in store.items()
                if assign.variable not in k.get_free_symbols()
            }

        return new_assignments
