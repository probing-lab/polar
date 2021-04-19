from diofant import Expr

from program import Program


class RecBuilder:

    program: Program

    def __init__(self, program: Program):
        self.program = program

    def get_recurrences(self, monomial: Expr):
        pass
