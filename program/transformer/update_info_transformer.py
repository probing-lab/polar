from typing import Set
from symengine.lib.symengine_wrapper import Symbol
from itertools import combinations

from .exceptions import TransformException
from .transformer import Transformer
from program import Program
from unsolvable_analysis import SolvabilityChecker
from program.assignment import (
    DistAssignment,
    FunctionalAssignment,
    PolyAssignment,
    Assignment,
)
from program.condition import TrueCond
from dataclasses import dataclass, field


class UpdateInfoTransformer(Transformer):
    """
    Prepares some final data about the program. So it can be better processed afterwards.
    The transformer requires that the passed program is already flattened, meaning does not contain any if-statements.
    """

    program: Program
    ignore_unsolvability: bool

    def __init__(self, ignore_unsolvability: bool = False):
        self.ignore_unsolvability = ignore_unsolvability

    def execute(self, program: Program) -> Program:
        self.program = program
        self._set_variables_and_symbols()
        self._set_dists_for_func_assignments(self.program.initial)
        self._set_dists_for_func_assignments(self.program.loop_body)
        self._set_dependencies()
        if not self.ignore_unsolvability:
            self._set_effective_defective_variables()
        return program

    def _set_variables_and_symbols(self):
        variables_initial = [a.variable for a in self.program.initial]
        variables_body = []
        self.program.dist_variables = []
        for assign in self.program.loop_body:
            variables_body.append(assign.variable)
            if isinstance(assign, DistAssignment):
                self.program.dist_variables.append(assign.variable)
            if isinstance(assign, FunctionalAssignment):
                self.program.func_variables.append(assign.variable)
        self.program.variables = set(variables_initial) | set(variables_body)
        self.program.var_to_index = {v: i for i, v in enumerate(variables_body)}
        self.program.index_to_var = {i: v for i, v in enumerate(variables_body)}

        symbols = self._get_all_symbols(self.program.initial)
        symbols = symbols.union(self._get_all_symbols(self.program.loop_body))
        self.program.symbols = symbols.difference(self.program.variables)
        self.program.original_variables = (
            self.program.original_variables & self.program.variables
        )

    def _set_dists_for_func_assignments(self, assignments_list: [Assignment]):
        """
        Assigns to functional assignments the distributions (or constants) of their arguments
        The arguments of functional assignments must be unconditioned distributions (with constant parameters)
        or constants.
        """
        uncond_vars_dist = (
            {}
        )  # store variables that are assigned unconditioned distributions
        uncond_vars_const = (
            {}
        )  # store variables that are assigned unconditioned constants
        uncond_references = (
            {}
        )  # stores unconditioned variables that reference to constants or distributions
        for assign in assignments_list:
            # Store unconditioned distributions
            if isinstance(assign, DistAssignment) and assign.condition == TrueCond():
                uncond_vars_dist[assign.variable] = assign.distribution
                continue
            # store unconditioned constants. If variable is just a reference to another variable we also save it.
            if isinstance(assign, PolyAssignment) and assign.condition == TrueCond():
                if assign.is_constant():
                    uncond_vars_const[assign.variable] = assign.polynomials[0]
                if assign.is_reference() and assign.polynomials[0] in uncond_vars_dist:
                    uncond_references[assign.variable] = assign.polynomials[0]
                if assign.is_reference() and assign.polynomials[0] in uncond_vars_const:
                    uncond_references[assign.variable] = assign.polynomials[0]
                if assign.is_reference() and assign.polynomials[0] in uncond_references:
                    uncond_references[assign.variable] = uncond_references[
                        assign.polynomials[0]
                    ]
                continue

            # Assign to functional assignment the distribution or the constant of the argument
            if isinstance(assign, FunctionalAssignment):
                # if argument is a number => perfect
                if assign.argument.is_Number:
                    continue
                # if argument is a reference replace argument by the actual constant or dist
                if assign.argument in uncond_references:
                    assign.argument = uncond_references[assign.argument]
                # if argument refers to a constant replace argument by the constant
                if assign.argument in uncond_vars_const:
                    assign.argument = uncond_vars_const[assign.argument]
                    continue
                # if argument refers to a distribution, pass the distribution to the assignment
                if assign.argument in uncond_vars_dist:
                    assign.argument_dist = uncond_vars_dist[assign.argument]
                    continue
                # Every functional assignment has to be assigned a distribution or constant of its argument
                raise TransformException(
                    f"{assign.argument} in func assignment for {assign.variable} does not have an unconditional distribution"
                )

    def _set_dependencies(self):
        self.program.dependency_info = {
            v: DependencyInfo() for v in self.program.variables
        }
        handled_variables = set()

        # First initialize ancestors and previous iteration dependency check
        for assign in self.program.loop_body:
            info = self.program.dependency_info[assign.variable]
            parents = assign.get_free_symbols(with_default=False).difference(
                self.program.symbols
            )
            info.ancestors = parents.copy()
            for parent in parents:
                info.ancestors |= self.program.dependency_info[parent].ancestors
            info.iteration_dependent = not parents.issubset(handled_variables) or any(
                [self.program.dependency_info[p].iteration_dependent for p in parents]
            )
            info.dependencies = {assign.variable}
            handled_variables.add(assign.variable)

        # Then get dependencies from ancestors
        for v1, v2 in combinations(self.program.variables, 2):
            info1 = self.program.dependency_info[v1]
            info2 = self.program.dependency_info[v2]
            if info1.ancestors & info2.ancestors:
                info1.dependencies.add(v2)
                info2.dependencies.add(v1)

    def _get_all_symbols(self, assignments):
        all_symbols = set()
        for assign in assignments:
            all_symbols |= assign.get_free_symbols()
        return all_symbols

    def _set_effective_defective_variables(self):
        effective_vars, defective_vars = SolvabilityChecker.get_variables(self.program)
        self.program.effective_variables = effective_vars
        self.program.defective_variables = defective_vars


@dataclass
class DependencyInfo:
    ancestors: Set[Symbol] = field(default_factory=set)
    dependencies: Set[Symbol] = field(default_factory=set)
    iteration_dependent: bool = False
