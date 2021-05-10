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
        cond_subs = {}

        # Now, move the conditions of the if-statement into the conditions of the assignments
        not_previous = TrueCond()
        for i, branch in enumerate(branches):
            current_condition = conditions[i] if ifstmt.mutually_exclusive else And(not_previous, conditions[i])
            for assign in branch:
                assign.add_to_condition(current_condition.copy())
                assign.simplify_condition()
                # Remember variables which are appear a condition and are assigned within a branch
                if assign.variable in condition_symbols:
                    cond_subs[assign.variable] = get_unique_var(name="old")
            not_previous = And(not_previous, Not(conditions[i].copy()))
        all_assigns = [assign for branch in branches for assign in branch]

        # Use the old value in all conditions for variables which are assigned within a branch
        for assign in all_assigns:
            assign.condition.subs(cond_subs)

        # Before the if-statement we need to add assignments to actually store the old values of variables
        # appearing in conditions and being assigned within a branch
        rename_assigns = []
        for orig_var, new_var in cond_subs.items():
            rename_assigns.append(PolyAssignment.deterministic(new_var, orig_var))

        all_assigns = rename_assigns + all_assigns

        return tuple(all_assigns)

    def __get_all_symbols__(self, conditions: List[Condition]):
        all_symbols = set()
        for c in conditions:
            all_symbols |= c.get_free_symbols()
        return all_symbols
