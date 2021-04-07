from abc import ABC, abstractmethod


class Distribution(ABC):

    def __init__(self, parameters):
        self.set_parameters(parameters)
        super().__init__()

    @abstractmethod
    def set_parameters(self, parameters):
        pass

    @abstractmethod
    def get_moment(self, k: int):
        pass

    @abstractmethod
    def is_discrete(self) -> bool:
        pass
