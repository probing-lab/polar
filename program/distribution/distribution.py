from abc import ABC, abstractmethod
from typing import Optional, Type


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
    def get_type(self) -> Optional[Type]:
        pass

    @abstractmethod
    def is_discrete(self) -> bool:
        pass

    @abstractmethod
    def subs(self, substitutions):
        pass
