from symengine import symbols

from .transformer import Transformer
from program import Program


class MultiAssignTransformer(Transformer):
    """
    Ensures that all program variables have only one single assignment. It does so by introducing
    new variables and renaming. The transformer requires that the passed program is already
    flattened, meaning does not contain any if-statements.
    """

    def execute(self, program: Program) -> Program:
        assigns_per_var = self.__get_count_assign_per_var__(program)
        assigns_count = assigns_per_var.copy()

        substitutions = {}
        for assign in program.loop_body:
            assign.subs(substitutions)
            var = assign.variable
            if assigns_count[var] > 1:
                # Introduce new alias for var and from now on replace var with its alias
                new_var = symbols(
                    f"_{var}{assigns_per_var[var] - assigns_count[var] + 1}"
                )
                assign.variable = new_var
                substitutions[var] = new_var
                assigns_count[var] -= 1
            else:
                # No substitutions with var if we reached it's last assignment
                substitutions.pop(var, None)
        return program

    def __get_count_assign_per_var__(self, program: Program):
        counts = {}
        for assign in program.loop_body:
            if assign.variable in counts:
                counts[assign.variable] += 1
            else:
                counts[assign.variable] = 1
        return counts
