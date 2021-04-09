from abc import ABC
from functools import singledispatchmethod


class ProgramTransformer(ABC):

    def execute(self, element):
        if hasattr(element, "children"):
            for c in getattr(element, "children"):
                value = self.execute(getattr(element, c))
                setattr(element, c, value)

        return self.transform(element)

    @singledispatchmethod
    def transform(self, element):
        return element

    @transform.register
    def _(self, xs: list):
        result = []
        for x in xs:
            x = self.execute(x)
            if isinstance(x, list):
                result += x
            else:
                result.append(x)
        return result
