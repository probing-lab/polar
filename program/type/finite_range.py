from .finite import Finite


class FiniteRange(Finite):
    lower: int
    upper: int

    def __init__(self, parameters, variable=None):
        if len(parameters) != 2:
            raise RuntimeError("FiniteRange type requires 2 parameters")
        self.lower = int(parameters[0])
        self.upper = int(parameters[1])
        super().__init__(list(range(self.lower, self.upper + 1)), variable)

    def __str__(self):
        return f"{self.variable} : FiniteRange({self.lower}, {self.upper})"
