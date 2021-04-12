from .condition import Condition


class TrueCond(Condition):
    def __str__(self):
        return "true"

    def simplify(self):
        return self
