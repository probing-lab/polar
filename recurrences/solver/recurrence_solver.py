from recurrences import Recurrences
from .acyclic_solver import AcyclicSolver
from .cyclic_solver import CyclicSolver
from .solver import Solver


class RecurrenceSolver(Solver):
    solver: Solver

    def __init__(
        self,
        recurrences: Recurrences,
        numeric_roots: bool,
        numeric_croots: bool,
        numeric_eps: float,
        force_cyclic_solver: bool = False,
    ):
        if recurrences.is_acyclic and not force_cyclic_solver:
            self.solver = AcyclicSolver(recurrences)
        else:
            self.solver = CyclicSolver(
                recurrences, numeric_roots, numeric_croots, numeric_eps
            )

    @property
    def is_exact(self) -> bool:
        return self.solver.is_exact

    def get(self, monomial):
        return self.solver.get(monomial)
