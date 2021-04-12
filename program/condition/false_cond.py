from .condition import Condition


class FalseCond(Condition):
    def __str__(self):
        return "false"

    def simplify(self):
        return self
