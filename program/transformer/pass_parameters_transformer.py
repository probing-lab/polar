from typing import List

from .transformer import Transformer
from program import Program
from program.assignment import Assignment, FunctionalAssignment


class PassParametersTransformer(Transformer):
    """
    Passes certain parameters to different parts of the program
    """
    exact_func_moments: bool

    def __init__(self, exact_func_moments: bool = False):
        self.exact_func_moments = exact_func_moments

    def execute(self, program: Program) -> Program:
        self.__pass_params_to_func_assigns(self.exact_func_moments, program.initial)
        self.__pass_params_to_func_assigns(self.exact_func_moments, program.loop_body)
        return program

    def __pass_params_to_func_assigns(self, exact_func_moments: bool, assigns: List[Assignment]):
        for assign in assigns:
            if isinstance(assign, FunctionalAssignment):
                assign.exact_moments = exact_func_moments
