from abc import ABC, abstractmethod


class ProgramTransformer(ABC):

    def __init__(self):
        @self.__class__.transform.register
        def _(self, xs: list):
            result = []
            for x in xs:
                x = self.execute(x)
                if isinstance(x, tuple):
                    result += list(x)
                else:
                    result.append(x)
            return result

    def execute(self, element):
        if hasattr(element, "children"):
            for c in getattr(element, "children"):
                value = self.execute(getattr(element, c))
                setattr(element, c, value)

        return self.transform(element)

    @abstractmethod
    def transform(self, element):
        pass
