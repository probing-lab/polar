from typing import List, Tuple
from .transformer import Transformer
from program import Program
from program.condition import Condition, TrueCond, And
from program.ifstatem import IfStatem


class LoopGuardTransformer(Transformer):
    """
    Transforms a program from "while guard: ..." to "while true: if guard: ..."
    Also it collapses simple top-level if-statements into a single if. For example:
    if cond1: if cond2: stuff end end
    turns into
    if cond1 and cond2: stuff end
    """

    trivial_guard: bool = False

    def __init__(self, trivial_guard: bool):
        self.trivial_guard = trivial_guard

    def execute(self, program: Program) -> Program:
        if self.trivial_guard:
            program.loop_guard = TrueCond()
            return program

        statements, condition = self._collapse_first_level_ifs(program.loop_body)
        condition = And(program.loop_guard, condition).simplify()
        program.loop_guard = TrueCond()
        condition.is_loop_guard = True
        if not isinstance(condition, TrueCond):
            program.loop_body = [IfStatem([condition], [statements])]
        return program

    def _collapse_first_level_ifs(self, statements: List) -> Tuple[List, Condition]:
        if len(statements) != 1 or not isinstance(statements[0], IfStatem):
            return statements, TrueCond()

        if_statem: IfStatem = statements[0]
        if len(if_statem.branches) != 1 or if_statem.else_branch:
            return statements, TrueCond()

        branch_statms, branch_cond = self._collapse_first_level_ifs(
            if_statem.branches[0]
        )
        condition = And(branch_cond, if_statem.conditions[0]).simplify()

        return branch_statms, condition
