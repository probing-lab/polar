from abc import ABC, abstractmethod


class Solver(ABC):

    @property
    @abstractmethod
    def is_exact(self) -> bool:
        pass

    @abstractmethod
    def get(self, monomial):
        pass
