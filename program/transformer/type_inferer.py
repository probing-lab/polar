from .transformer import Transformer
from program import Program


class TypeInferer(Transformer):
    """
    Infers potential types of program variables and adds them to the program's type registry.
    The transformer requires that the passed program is flattened, meaning it does not contain any if-statements.
    TODO: The current implementation is rudimentary and needs to be extended in the future.
    """

    def execute(self, program: Program) -> Program:
        for assign in program.loop_body:
            assign_type = assign.get_assign_type()
            if assign_type:
                assign_type.expression = assign.variable
                program.add_type(assign_type)
        return program
