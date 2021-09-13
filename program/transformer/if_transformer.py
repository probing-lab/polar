from typing import List

from singledispatchmethod import singledispatchmethod

from program.condition import TrueCond, And, Not, Condition
from program.ifstatem import IfStatem
from program.assignment import Assignment, PolyAssignment
from program.transformer.transformer import TreeTransformer
from utils import get_unique_var


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
        branches: List[List[Assignment]] = ifstmt.branches
        if ifstmt.else_branch:
            branches.append(ifstmt.else_branch)
            conditions.append(TrueCond())

        # If a variable in a condition is assigned within a branch we need to store its old value at the beginning
        # and use the old value in all conditions
        condition_symbols = self.__get_all_symbols__(conditions)
        rename_subs = {}

        # Now, move the conditions of the if-statement into the conditions of the assignments
        not_previous = TrueCond()
        for i, branch in enumerate(branches):
            current_condition = conditions[i] if ifstmt.mutually_exclusive else And(not_previous, conditions[i])

            # Remember variables which appear in a condition and are assigned within the branch
            current_rename_subs = {}
            for assign in branch:
                if assign.variable in condition_symbols:
                    if assign.variable in rename_subs:
                        current_rename_subs[assign.variable] = rename_subs[assign.variable]
                    else:
                        current_rename_subs[assign.variable] = get_unique_var(name="old")
                        rename_subs[assign.variable] = current_rename_subs[assign.variable]
            extra_condition = current_condition.copy()
            extra_condition.subs(current_rename_subs)

            # Add the branch conditions to the assignments
            for assign in branch:
                assign.add_to_condition(extra_condition)
                assign.simplify_condition()

            not_previous = And(not_previous, Not(conditions[i].copy()))
        all_assigns = [assign for branch in branches for assign in branch]

        # Before the if-statement we need to add assignments to actually store the old values of variables
        # appearing in conditions and being assigned within a branch
        rename_assigns = []
        for orig_var, new_var in rename_subs.items():
            rename_assigns.append(PolyAssignment.deterministic(new_var, orig_var))

        all_assigns = rename_assigns + all_assigns

        return tuple(all_assigns)

    def __get_all_symbols__(self, conditions: List[Condition]):
        all_symbols = set()
        for c in conditions:
            all_symbols |= c.get_free_symbols()
        return all_symbols
