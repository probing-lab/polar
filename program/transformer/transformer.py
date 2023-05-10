from abc import ABC, abstractmethod

from program import Program


class Transformer(ABC):
    """
    Abstract class for transformers which transform a program into another possibly equivalent program
    """

    @abstractmethod
    def execute(self, program: Program) -> Program:
        pass


class TreeTransformer(Transformer, ABC):
    """
    Abstract class for transformers acting on the deep tree structure of a program by providing methods
    which transform individual nodes.
    """

    program: Program

    def __init__(self):
        @self.__class__.transform.register
        def _(self, xs: list):
            result = []
            for x in xs:
                x = self._execute(x)
                if isinstance(x, tuple):
                    result += list(x)
                else:
                    result.append(x)
            return result

    def execute(self, program: Program) -> Program:
        self.program = program
        return self._execute(program)

    def _execute(self, element):
        if hasattr(element, "children"):
            for c in getattr(element, "children"):
                value = self._execute(getattr(element, c))
                setattr(element, c, value)

        return self.transform(element)

    @abstractmethod
    def transform(self, element):
        pass
