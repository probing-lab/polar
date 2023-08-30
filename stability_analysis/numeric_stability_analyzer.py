from functools import lru_cache
from recurrences import Recurrences
from stability_analysis.stability_analyzer import StabilityAnalyzer
import numpy as np


class NumericStabilityAnalyzer(StabilityAnalyzer):

    recurrences: Recurrences
    A: np.ndarray
    b: np.ndarray

    def __init__(self, recurrences: Recurrences):
        self.recurrences = recurrences
        self.A = np.array(self.recurrences.A).astype(np.float64)
        self.b = np.array(self.recurrences.b).astype(np.float64)

    @lru_cache(maxsize=None)
    def _get_eigenvalues(self):
        eigvs = np.linalg.eigvals(self.A)
        result = {}
        for ev in eigvs:
            if ev in result:
                result[ev] += 1
            else:
                result[ev] = 1
        return result

    @lru_cache(maxsize=None)
    def get_rho(self):
        eigvs = self._get_eigenvalues()
        return max([abs(ev) for ev in eigvs.keys()])

    @lru_cache(maxsize=None)
    def is_globally_stable(self) -> bool:
        eigvs = self._get_eigenvalues()
        return all([abs(ev) < 1 for ev in eigvs.keys()])

    @lru_cache(maxsize=None)
    def is_unstable(self) -> bool:
        eigvs = self._get_eigenvalues()
        return any([abs(ev) > 1 for ev in eigvs.keys()])

    @lru_cache(maxsize=None)
    def is_lyapunov_stable(self) -> bool:
        if self.is_globally_stable():
            return True
        eigvs = self._get_eigenvalues()
        if any([mult > 1 for mult in eigvs.values()]):
            return False
        return all([c <= 1 for c in eigvs.keys()])

    @lru_cache(maxsize=None)
    def get_equilibrium(self):
        I = np.identity(self.A.shape[0])
        return np.dot(np.linalg.inv(I - self.A), self.b)
