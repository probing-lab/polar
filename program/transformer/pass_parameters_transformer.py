from typing import List

from .transformer import Transformer
from program import Program
from program.assignment import Assignment, TrigAssignment


class PassParametersTransformer(Transformer):
    """
    Passes certain parameters to different parts of the program
    """
    exact_transc_moments: bool

    def __init__(self, exact_transc_moments: bool = False):
        self.exact_transc_moments = exact_transc_moments

    def execute(self, program: Program) -> Program:
        self.__pass_params_to_trig_assigns(self.exact_transc_moments, program.initial)
        self.__pass_params_to_trig_assigns(self.exact_transc_moments, program.loop_body)
        return program

    def __pass_params_to_trig_assigns(self, exact_transc_moments: bool, assigns: List[Assignment]):
        for assign in assigns:
            if isinstance(assign, TrigAssignment):
                assign.exact_transcendentals = exact_transc_moments
