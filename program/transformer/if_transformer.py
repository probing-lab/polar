from functools import singledispatchmethod

from program.condition import TrueCond, And, Not
from program.ifstatem import IfStatem
from program.transformer.transformer import TreeTransformer


class IfTransformer(TreeTransformer):
    """
    Removes all if-statements from the program and moves the branch conditions into the conditions
    of the assignments. So the transformer basically flattens the structure.
    """

    @singledispatchmethod
    def transform(self, element):
        return element

    @transform.register
    def _(self, ifstmt: IfStatem):
        conditions = ifstmt.conditions
        branches = ifstmt.branches

        not_previous = TrueCond()
        for i, branch in enumerate(branches):
            current_condition = And(not_previous, conditions[i])
            for assign in branch:
                assign.add_to_condition(current_condition)
                assign.simplify_condition()
            not_previous = And(not_previous, Not(conditions[i]))

        all_assigns = [assign for branch in branches for assign in branch]
        if ifstmt.else_branch:
            for assign in ifstmt.else_branch:
                assign.add_to_condition(not_previous)
                assign.simplify_condition()
            all_assigns += ifstmt.else_branch

        return tuple(all_assigns)
