from functools import reduce
from typing import Dict, List, Tuple
from bayes_network import BayesNetwork
from bayes_variable import BayesVariable
from itertools import product
import queue

# TODO: rename variables in polar, rename domain-elements to numbers

class CodeGenerator:
    network: BayesNetwork

    def __init__(self, network: BayesNetwork):
        self.network = network

    def generate_code(self) -> str:
        return '\n'.join(self.__generate_init__() + self.__generate_loop__())

    def __generate_init__(self) -> List[str]:
        init_code: List[str] = []
        for v in self.network.variables.values():
            init_code.append(v.name + " = " + v.domain[0])
        return init_code

    def __generate_loop__(self) -> List[str]:
        loop_code: List[str] = ["while true:"]
        for v in self.__topological_sort__(list(self.network.variables.values())):
            loop_code += self.__generate_variable__(v)
            loop_code.append("")
        loop_code.append("end")
        return loop_code

    def __generate_variable__(self, var: BayesVariable) -> List[str]:
        indent = "\t"
        statements = [indent + "# variable: " + var.name]
        if len(var.parents) == 0:
            statements.append(indent + self.__generate_assignment__(var, ()))
        else:
            parent_domains: List[Tuple[str]] = [p.domain for p in var.parents]
            num_combinations = reduce(lambda x, y: x*y, [p.domain_size for p in var.parents], 1)
            for comb_idx, comb in enumerate(product(*parent_domains)):
                is_first = comb_idx == 0
                is_last = comb_idx == num_combinations - 1
                condition = self.__generate_condition__(var, comb, is_first, is_last)
                statements.append(indent + condition)
                statements.append(indent*2 + self.__generate_assignment__(var, comb))
                if is_last:
                    statements.append(indent + "end")
        return statements

    def __generate_condition__(self, var: BayesVariable, comb: Tuple[str], is_first: bool, is_last: bool) -> str:
        if is_first:
            condition = "if "
        elif is_last:
            return "else: "
        else:
            condition = "elif "

        for i in range(len(comb) - 1):
            condition += var.parents[i].name + " == " + comb[i] + " && "

        return condition + var.parents[-1].name + " == " + comb[-1] + ":"

    def __generate_assignment__(self, var: BayesVariable, comb: Tuple[str]) -> str:
        assignment = var.name + " = "
        for i in range(len(var.domain) - 1):
            assignment += var.domain[i] + " {" + str(var.cpt[comb][i]) + "} "
        return assignment + var.domain[-1]

    def __topological_sort__(self, variables: List[BayesVariable]) -> List[BayesVariable]:
        num_parents: List[int] = [v.num_parents for v in variables]
        sources: queue.Queue = queue.Queue()
        topological_sort: List[BayesVariable] = []

        for i in range(len(variables)):
            if num_parents[i] == 0:
                sources.put(variables[i])

        while(not sources.empty()):
            source = sources.get()
            topological_sort.append(source)
            for i in range(len(variables)):
                if source in variables[i].parents:
                    num_parents[i] = num_parents[i] - 1
                    if num_parents[i] == 0:
                        sources.put(variables[i])

        assert(len(topological_sort) == len(num_parents))
        return topological_sort
