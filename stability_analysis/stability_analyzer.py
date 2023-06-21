from abc import ABC, abstractmethod


class StabilityAnalyzer(ABC):
    @abstractmethod
    def is_globally_stable(self) -> bool:
        pass

    @abstractmethod
    def is_unstable(self) -> bool:
        pass

    @abstractmethod
    def is_lyapunov_stable(self) -> bool:
        pass

    @abstractmethod
    def get_equilibrium(self):
        pass
