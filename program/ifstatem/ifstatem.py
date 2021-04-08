from program.condition import Condition


class IfStatem:
    conditions: [Condition]
    branches: []
    else_branch = None

    def __init__(self, conditions, branches, else_branch=None):
        self.conditions = conditions
        self.branches = branches
        self.else_branch = else_branch
