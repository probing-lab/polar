from abc import ABC, abstractmethod
from typing import List
from program import Program
from program.type import Type


class Typer(ABC):
    @abstractmethod
    def infer_types(self, program: Program) -> List[Type]:
        pass
