from program.condition import Condition


class Not(Condition):
    cond: Condition

    def __init__(self, cond):
        self.cond = cond
