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
                x = self.__execute__(x)
                if isinstance(x, tuple):
                    result += list(x)
                else:
                    result.append(x)
            return result

    def execute(self, program: Program) -> Program:
        self.program = program
        return self.__execute__(program)

    def __execute__(self, element):
        if hasattr(element, "children"):
            for c in getattr(element, "children"):
                value = self.__execute__(getattr(element, c))
                setattr(element, c, value)

        return self.transform(element)

    @abstractmethod
    def transform(self, element):
        pass
