from typing import Set
from symengine.lib.symengine_wrapper import Symbol
from itertools import combinations

from .transformer import Transformer
from program import Program
from dataclasses import dataclass, field


class UpdateInfoTransformer(Transformer):
    """
    Prepares some final data about the program. So it can be better processed afterwards.
    The transformer requires that the passed program is already flattened, meaning does not contain any if-statements.
    """
    program: Program

    def execute(self, program: Program) -> Program:
        self.program = program
        self.__set_variables_and_symbols__()
        self.__set_dependencies__()
        return program

    def __set_variables_and_symbols__(self):
        variables_initial = self.__get_all_variables__(self.program.initial)
        variables_body = self.__get_all_variables__(self.program.loop_body)
        self.program.variables = set(variables_initial) | set(variables_body)
        self.program.var_to_index = {v: i for i, v in enumerate(variables_body)}
        self.program.index_to_var = {i: v for i, v in enumerate(variables_body)}

        symbols = self.__get_all_symbols__(self.program.initial)
        symbols = symbols.union(self.__get_all_symbols__(self.program.loop_body))
        self.program.symbols = symbols.difference(self.program.variables)

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

    def __get_all_variables__(self, assignments):
        return [a.variable for a in assignments]

    def __get_all_symbols__(self, assignments):
        all_symbols = set()
        for assign in assignments:
            all_symbols |= assign.get_free_symbols()
        return all_symbols


@dataclass
class DependencyInfo:
    ancestors: Set[Symbol] = field(default_factory=set)
    dependencies: Set[Symbol] = field(default_factory=set)
    iteration_dependent: bool = False