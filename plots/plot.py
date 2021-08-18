from abc import ABC, abstractmethod


class Plot(ABC):

    @abstractmethod
    def save(self, filename: str):
        pass

    @abstractmethod
    def draw(self):
        pass
