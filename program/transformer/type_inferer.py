import settings
from type_inference import FiniteFixedPointTyper
from .transformer import Transformer
from program import Program


class TypeInferer(Transformer):
    """
    Infers potential types of program variables and adds them to the program's type registry.
    The transformer requires that the passed program is flattened, meaning it does not contain any if-statements.
    Moreover, every variable is assumed to have only a single assignment.
    """

    def __init__(self, fp_iterations: int = -1):
        self.fp_iterations = (
            settings.type_fp_iterations if fp_iterations < 0 else fp_iterations
        )

    def execute(self, program: Program) -> Program:
        typer = FiniteFixedPointTyper(self.fp_iterations)
        for t in typer.infer_types(program):
            program.add_type(t)
        return program
