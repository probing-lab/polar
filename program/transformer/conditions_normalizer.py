from typing import List, Set, Dict

from symengine.lib.symengine_wrapper import Symbol, One

from .update_info_transformer import UpdateInfoTransformer
from .exceptions import NormalizingException
from .transformer import Transformer
from program import Program
from program.assignment import Assignment, DistAssignment
from program.condition import Condition, Atom, TrueCond, And
from utils import get_unique_var
from program.distribution import Bernoulli
from program.type import Finite


class ConditionsNormalizer(Transformer):
    """
    Normalizes the conditions in the program. That means that inequalities are replaced by conjunctions of
    equalities for finitely typed variables. For variables which are not finitely typed the transformer
    abstracts conditions as bernoulli events if possible.
    The transformer requires that the passed program is flattened, meaning it does not contain any if-statements.
    Also all conditions are assumed to be reduced (see transformer ConditionsReducer)
    """

    program: Program
    needs_info_update: bool = False

    def execute(self, program: Program) -> Program:
        self.program = program
        self.program.initial = self.__normalize_conditions__(self.program.initial)
        self.program.loop_body = self.__normalize_conditions__(self.program.loop_body)
        if self.program.original_loop_guard is None:
            self.program.original_loop_guard = TrueCond()
        if self.needs_info_update:
            program = UpdateInfoTransformer().execute(program)
        return program

    def __normalize_conditions__(self, assignments: List[Assignment]):
        new_assignments = []
        already_assigned_vars = set()
        abstracted_vars = set()
        store = {}
        for assign in assignments:
            store = {
                k: v
                for k, v in store.items()
                if assign.variable not in k.get_free_symbols()
            }
            normalized_condition, failed_atoms = assign.condition.get_normalized(
                self.program
            )
            assign.condition = normalized_condition
            if failed_atoms:
                self.__try_abstract_failed_condition__(
                    assign,
                    failed_atoms,
                    already_assigned_vars,
                    store,
                    new_assignments,
                    abstracted_vars,
                )
                self.needs_info_update = True
            new_assignments.append(assign)
            already_assigned_vars.add(assign.variable)
            if self.program.original_loop_guard is None:
                self.program.original_loop_guard = assign.condition.get_loop_guard()
        return new_assignments

    def __try_abstract_failed_condition__(
        self,
        assign: Assignment,
        failed_atoms: List[Atom],
        already_assigned_vars: Set[Symbol],
        abstraction_store: Dict[Condition, Symbol],
        new_assignments: List[Assignment],
        abstracted_vars: Set[Symbol],
    ):
        """
        Basic idea: If an atom "failed" we have to consider the whole conjunct it appears in as "failed",
        because separating them out of disjunctions would be be a mess. Then we are basically left
        with one bad condition C = Bad1 and Bad2 and Bad3 ... and Badk
        Now the following has to hold

        1. C is iteration independent
        2. C is independent of variables in assignment which were already assigned in this iteration
        3. C is independent of variables in good condition part which have already been assigned.

        Then we can replace C by Bernoulli(p) == 1 where p = P(C at current pos)
        If C already has been abstracted as Bernoulli(p) and none of the variables in C have been reassigned since
        then we use the old abstraction. If the have been reassigned we need to introduce a new abstraction.
        """
        failed_variables = {v for a in failed_atoms for v in a.get_free_symbols()}
        good_condition, bad_condition = self.__partition_condition__(
            assign.condition, failed_variables
        )
        bad_is_iter_dependent = any(
            [
                self.program.is_iteration_dependent(v)
                for v in bad_condition.get_free_symbols()
            ]
        )
        if bad_is_iter_dependent:
            raise NormalizingException(
                f"Can't normalize condition {bad_condition}, because iteration dependency."
            )

        assign_vars = assign.get_free_symbols(with_condition=False).difference(
            self.program.symbols
        )
        good_cond_vars = good_condition.get_free_symbols()
        forbidden_variables = (assign_vars | good_cond_vars).intersection(
            already_assigned_vars
        )
        if self.program.is_dependent_vars(
            bad_condition.get_free_symbols(), forbidden_variables
        ):
            raise NormalizingException(
                f"Can't normalize condition {bad_condition}, because of variable dependency."
            )

        if bad_condition not in abstraction_store:
            if self.program.is_dependent_vars(
                bad_condition.get_free_symbols(), abstracted_vars
            ):
                raise NormalizingException(
                    f"Can't normalize condition {bad_condition}, "
                    f"because of variable dependency between abstracted variables"
                )
            new_var = Symbol(get_unique_var(name="a"))
            new_prob = Symbol(get_unique_var(name="prob"))
            abstraction_assign = DistAssignment(new_var, Bernoulli([new_prob]))
            self.program.add_type(Finite([0, 1], new_var))
            abstraction_store[bad_condition] = new_var
            new_assignments.append(abstraction_assign)
            self.program.abstracted_const_store[new_prob] = bad_condition.copy()
            abstraction_store[bad_condition] = new_var
            abstracted_vars |= bad_condition.get_free_symbols()

        assign.condition = And(
            good_condition, Atom(abstraction_store[bad_condition], "==", One())
        ).simplify()

    def __partition_condition__(
        self, condition: Condition, failed_variables: Set[Symbol]
    ):
        good_condition = TrueCond()
        bad_condition = TrueCond()
        for conjunct in condition.get_conjuncts():
            if not conjunct.get_free_symbols().intersection(failed_variables):
                good_condition = And(good_condition, conjunct)
            else:
                bad_condition = And(bad_condition, conjunct)

        return good_condition.simplify(), bad_condition.simplify()
