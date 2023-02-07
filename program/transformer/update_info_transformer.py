from typing import Set
from symengine.lib.symengine_wrapper import Symbol
from itertools import combinations

from .exceptions import TransformException
from .transformer import Transformer
from program import Program
from program.mc_checker import MCChecker
from program.assignment import DistAssignment, TrigAssignment, PolyAssignment, Assignment
from program.condition import TrueCond
from dataclasses import dataclass, field


class UpdateInfoTransformer(Transformer):
    """
    Prepares some final data about the program. So it can be better processed afterwards.
    The transformer requires that the passed program is already flattened, meaning does not contain any if-statements.
    """
    program: Program
    ignore_mc_variables: bool

    def __init__(self, ignore_mc_variables: bool = False):
        self.ignore_mc_variables = ignore_mc_variables

    def execute(self, program: Program) -> Program:
        self.program = program
        self.__set_variables_and_symbols__()
        self.__set_dists_for_trig_assignments__(self.program.initial)
        self.__set_dists_for_trig_assignments__(self.program.loop_body)
        self.__set_dependencies__()
        if not self.ignore_mc_variables:
            self.__set_mc_variables__()
        return program

    def __set_variables_and_symbols__(self):
        variables_initial = [a.variable for a in self.program.initial]
        variables_body = []
        self.program.dist_variables = []
        for assign in self.program.loop_body:
            variables_body.append(assign.variable)
            if isinstance(assign, DistAssignment):
                self.program.dist_variables.append(assign.variable)
            if isinstance(assign, TrigAssignment):
                self.program.trig_variables.append(assign.variable)
        self.program.variables = set(variables_initial) | set(variables_body)
        self.program.var_to_index = {v: i for i, v in enumerate(variables_body)}
        self.program.index_to_var = {i: v for i, v in enumerate(variables_body)}

        symbols = self.__get_all_symbols__(self.program.initial)
        symbols = symbols.union(self.__get_all_symbols__(self.program.loop_body))
        self.program.symbols = symbols.difference(self.program.variables)
        self.program.original_variables = self.program.original_variables & self.program.variables

    def __set_dists_for_trig_assignments__(self, assignments_list: [Assignment]):
        uncond_vars_dist = {}
        uncond_vars_const = {}
        for assign in assignments_list:
            if isinstance(assign, DistAssignment) and assign.condition == TrueCond():
                uncond_vars_dist[assign.variable] = assign.distribution
            if isinstance(assign, PolyAssignment) and assign.is_constant() and assign.condition == TrueCond():
                uncond_vars_const[assign.variable] = assign.polynomials[0]
            if isinstance(assign, TrigAssignment):
                if assign.argument.is_Number:
                    break
                if assign.argument in uncond_vars_dist:
                    assign.argument_dist = uncond_vars_dist[assign.argument]
                    break
                if assign.argument in uncond_vars_const:
                    assign.argument = uncond_vars_const[assign.argument]
                    break
                raise TransformException(f"{assign.argument} in trig assignment for {assign.variable} does not have an unconditional distribution")

    def __set_dependencies__(self):
        self.program.dependency_info = {v: DependencyInfo() for v in self.program.variables}
        handled_variables = set()

        # First initialize ancestors and previous iteration dependency check
        for assign in self.program.loop_body:
            info = self.program.dependency_info[assign.variable]
            parents = assign.get_free_symbols(with_default=False).difference(self.program.symbols)
            info.ancestors = parents.copy()
            for parent in parents:
                info.ancestors |= self.program.dependency_info[parent].ancestors
            info.iteration_dependent =\
                not parents.issubset(handled_variables) or\
                any([self.program.dependency_info[p].iteration_dependent for p in parents])
            info.dependencies = {assign.variable}
            handled_variables.add(assign.variable)

        # Then get dependencies from ancestors
        for v1, v2 in combinations(self.program.variables, 2):
            info1 = self.program.dependency_info[v1]
            info2 = self.program.dependency_info[v2]
            if info1.ancestors & info2.ancestors:
                info1.dependencies.add(v2)
                info2.dependencies.add(v1)

    def __get_all_symbols__(self, assignments):
        all_symbols = set()
        for assign in assignments:
            all_symbols |= assign.get_free_symbols()
        return all_symbols

    def __set_mc_variables__(self):
        mc_vars, non_mc_vars = MCChecker.get_mc_variables(self.program)
        self.program.mc_variables = mc_vars
        self.program.non_mc_variables = non_mc_vars


@dataclass
class DependencyInfo:
    ancestors: Set[Symbol] = field(default_factory=set)
    dependencies: Set[Symbol] = field(default_factory=set)
    iteration_dependent: bool = False
