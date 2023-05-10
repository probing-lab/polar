from typing import List
from program.condition import Condition
from utils import indent_string


class IfStatem:
    conditions: List[Condition]
    mutually_exclusive: bool  # Flag to signal that all conditions are mutually exclusive
    branches: List
    else_branch = None

    children = ["branches", "else_branch"]

    def __init__(
        self, conditions, branches, else_branch=None, mutually_exclusive=False
    ):
        self.conditions = conditions
        self.branches = branches
        self.else_branch = else_branch
        self.mutually_exclusive = mutually_exclusive

    def __str__(self):
        def branch_to_str(branch):
            return indent_string("\n".join([str(b) for b in branch]), 4)

        string = f"if {self.conditions[0]}:\n{branch_to_str(self.branches[0])}"
        for i, branch in enumerate(self.branches[1:], start=1):
            string += f"\nelse if {self.conditions[i]}:\n{branch_to_str(branch)}"
        if self.else_branch:
            string += f"\nelse:\n{branch_to_str(self.else_branch)}"

        return string
