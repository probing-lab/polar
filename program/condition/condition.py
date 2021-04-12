from abc import ABC, abstractmethod


class Condition(ABC):

    @abstractmethod
    def simplify(self):
        pass
