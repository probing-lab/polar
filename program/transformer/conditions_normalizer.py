from typing import List, Set

from symengine.lib.symengine_wrapper import Symbol

from .exceptions import NormalizingException
from .transformer import Transformer
from program import Program
from ..assignment import Assignment
from ..condition import Condition


class ConditionsNormalizer(Transformer):
    """
    Bla
    """
    program: Program

    def execute(self, program: Program) -> Program:
        self.program = program
        self.__normalize_conditions__(self.program.initial)
        self.__normalize_conditions__(self.program.loop_body)
        return program

    def __normalize_conditions__(self, assignments: List[Assignment]):
        for assign in assignments:
            normalized_condition, failed_atoms = assign.condition.get_normalized(self.program)
            assign.condition = normalized_condition
            if failed_atoms:
                failed_variables = {atom.poly1 for atom in failed_atoms}
                self.__try_abstract_failed_condition__(assign, failed_variables)

    def __try_abstract_failed_condition__(self, assign: Assignment, failed_variables: Set[Symbol]):
        good_conjuncts, bad_conjuncts = self.__partition_conjuncts__(assign.condition, failed_variables)
        failed_variables = {v for c in bad_conjuncts for v in c.get_free_symbols()}
        # TODO: continue
        pass

    def __partition_conjuncts__(self, condition: Condition, failed_variables: Set[Symbol]):
        good_conjuncts = []
        bad_conjuncts = []
        for conjunct in condition.get_conjuncts():
            if not conjunct.get_free_symbols().intersection(failed_variables):
                good_conjuncts.append(conjunct)
            else:
                bad_conjuncts.append(conjunct)

        return good_conjuncts, bad_conjuncts
