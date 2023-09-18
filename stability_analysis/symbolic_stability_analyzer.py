from functools import lru_cache
from sympy import eye, Max
from recurrences import Recurrences
from stability_analysis.stability_analyzer import StabilityAnalyzer


class SymbolicStabilityAnalyzer(StabilityAnalyzer):
    recurrences: Recurrences

    def __init__(self, recurrences: Recurrences):
        self.recurrences = recurrences

    @lru_cache(maxsize=None)
    def _get_eigenvalues(self):
        return self.recurrences.A.eigenvals()

    @lru_cache(maxsize=None)
    def _compare_eigenvalues_with(self, k: int):
        return [abs(ev).compare(k) for ev in self._get_eigenvalues().keys()]

    @lru_cache(maxsize=None)
    def get_rho(self):
        eigvs = self._get_eigenvalues()
        return Max(*[abs(ev) for ev in eigvs.keys()])

    @lru_cache(maxsize=None)
    def is_globally_stable(self) -> bool:
        comparisons = self._compare_eigenvalues_with(1)
        return all([c == -1 for c in comparisons])

    @lru_cache(maxsize=None)
    def is_unstable(self) -> bool:
        comparisons = self._compare_eigenvalues_with(1)
        return any([c == 1 for c in comparisons])

    @lru_cache(maxsize=None)
    def is_lyapunov_stable(self) -> bool:
        if self.is_globally_stable():
            return True
        eigv_multiplicities = self._get_eigenvalues().values()
        if any([m > 1 for m in eigv_multiplicities]):
            return False
        comparisons = self._compare_eigenvalues_with(1)
        return all([c <= 0 for c in comparisons])

    @lru_cache(maxsize=None)
    def get_equilibrium(self):
        A = self.recurrences.A
        b = self.recurrences.b
        I = eye(A.shape[0])
        return ((I - A) ** (-1)) * b
