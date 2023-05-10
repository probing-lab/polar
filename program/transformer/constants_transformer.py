from typing import List

from .transformer import Transformer
from program import Program
from program.assignment import PolyAssignment, Assignment
from program.condition import TrueCond


class ConstantsTransformer(Transformer):
    """
    Constants are variables not reassigned in the loop body. The transformer processes constants in two ways:
    1. If the constant is a single fixed value it removes its initial assignment and replaces it everywhere
    by its value.

    2. If the constant x is more than a single fixed value it adds the assignment x=x at the end of the loop body.

    The transformer requires that the program is flattened.
    """

    def execute(self, program: Program) -> Program:
        loop_body_vars = {a.variable for a in program.loop_body}
        fixed_constants = {}
        other_constants = set()

        new_initial_assignments = []
        for assign in program.initial:
            # Not constant
            if assign.variable in loop_body_vars:
                new_initial_assignments.append(assign)
                continue

            # Constant is a single fixed value
            if (
                isinstance(assign, PolyAssignment)
                and isinstance(assign.condition, TrueCond)
                and len(assign.polynomials) == 1
            ):
                fixed_constants[assign.variable] = assign.polynomials[0].subs(
                    fixed_constants
                )
                continue

            # Constant is not a single fixed value
            other_constants.add(assign.variable)
            new_initial_assignments.append(assign)

        program.initial = new_initial_assignments

        program.loop_guard.subs(fixed_constants)
        self._subs_in_assigns(program.initial, fixed_constants)
        self._subs_in_assigns(program.loop_body, fixed_constants)
        for c, v in fixed_constants.items():
            program.variables.remove(c)

        for c in other_constants:
            program.loop_body.append(PolyAssignment.deterministic(c, c))

        return program

    def _subs_in_assigns(self, assigns: List[Assignment], substitutions):
        for assign in assigns:
            assign.subs(substitutions)
