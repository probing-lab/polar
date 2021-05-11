from typing import List, Set

from symengine.lib.symengine_wrapper import Symbol

from .transformer import Transformer
from program import Program
from ..assignment import Assignment
from ..condition import Condition, Atom


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
                self.__try_abstract_failed_condition__(assign, failed_atoms)

    def __try_abstract_failed_condition__(self, assign: Assignment, failed_atoms: List[Atom]):
        failed_variables = {v for a in failed_atoms for v in a.get_free_symbols()}
        good_conjuncts, bad_conjuncts = self.__partition_conjuncts__(assign.condition, failed_variables)
        failed_variables = {v for c in bad_conjuncts for v in c.get_free_symbols()}
        # TODO
        # Basic idea: If an atom "failed" we have to consider the whole conjunct it appears in as "failed",
        # because separating them out of disjunctions would be be a mess. Then we are basically left
        # with one bad condition C = Bad1 and Bad2 and Bad3 ... and Badk
        # Now the following has to hold
        #
        # 1. C only depends is iteration independent
        # 2. C is independent of variables in assignment which were already assigned in this iteration
        # 3. C is independent of variables in good condition part which have already been assigned.
        #
        # Then we can replace C by Bernoulli(p) == 1 where p = P(C at current pos)
        # If C already has been abstracted as Bernoulli(p) and none of the variables in C have been reassigned since
        # then we use the old abstraction. If the have been reassigned we need to introduce a new abstraction.
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
