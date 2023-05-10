from functools import reduce
from typing import Dict, List, Tuple
from itertools import product
import queue
import re
from .bayes_network import BayesNetwork
from .bayes_variable import BayesVariable
from .common import get_unique_name
from .query.query import Query


class CodeGenerator:
    network: BayesNetwork
    query: Query
    polar_variable_names: Dict[
        str, str
    ]  # keys: bayes-net variables, values: polar-names

    # For variables, all chars except letters, numbers and underscores are removed,
    #  and if necessary random numbers are appened (so the variable is unique)
    # For domain elements, they get replaced by their index in the variable.domain tuple

    def __init__(self, network: BayesNetwork, query: Query = None):
        self.network = network
        self.query = query

    def generate_code(self) -> str:
        self.__generate_mapping__()
        return "\n".join(self.__generate_init__() + self.__generate_loop__())

    def __generate_mapping__(self):
        self.polar_variable_names = {}
        for varname in self.network.variables.keys():
            mapped_name = re.sub("[^A-Za-z0-9_]+", "", varname.lower())
            if mapped_name == "":
                mapped_name = "_"
            mapped_name = get_unique_name(
                self.polar_variable_names.values(), mapped_name
            )
            self.polar_variable_names[varname] = mapped_name

    def __generate_init__(self) -> List[str]:
        init_code: List[str] = []
        for v in self.network.variables.values():
            init_code.append(self.polar_variable_names[v.name] + " = 0")
        if self.query is not None:
            init_code += self.query.generate_init_code(
                self.network, self.polar_variable_names
            )
        return init_code

    def __generate_loop__(self) -> List[str]:
        loop_code: List[str] = ["while true:"]
        for v in self.__topological_sort__(list(self.network.variables.values())):
            loop_code += self.__generate_variable__(v)
            loop_code.append("")
        if self.query is not None:
            loop_code += self.query.generate_loop_code(
                self.network, self.polar_variable_names
            )
        loop_code.append("end")
        return loop_code

    def __generate_variable__(self, var: BayesVariable) -> List[str]:
        indent = "\t"
        statements = [
            indent
            + "# variable: "
            + var.name
            + " <=> "
            + self.polar_variable_names[var.name]
        ]
        if len(var.parents) == 0:
            statements.append(indent + self.__generate_assignment__(var, ()))
        else:
            parent_domains: List[Tuple[str]] = [p.domain for p in var.parents]
            num_combinations = reduce(
                lambda x, y: x * y, [p.domain_size for p in var.parents], 1
            )
            for comb_idx, comb in enumerate(product(*parent_domains)):
                is_first = comb_idx == 0
                is_last = comb_idx == num_combinations - 1
                condition = self.__generate_condition__(var, comb, is_first, is_last)
                statements.append(indent + condition)
                statements.append(indent * 2 + self.__generate_assignment__(var, comb))
                if is_last:
                    statements.append(indent + "end")
        return statements

    def __generate_condition__(
        self, var: BayesVariable, comb: Tuple[str], is_first: bool, is_last: bool
    ) -> str:
        if is_first:
            condition = "if "
        elif is_last:
            return "else: "
        else:
            condition = "elif "

        for i in range(len(comb) - 1):
            domain_index = var.parents[i].domain.index(comb[i])
            condition += (
                self.polar_variable_names[var.parents[i].name]
                + " == "
                + str(domain_index)
                + " && "
            )

        domain_index = var.parents[-1].domain.index(comb[-1])
        return (
            condition
            + self.polar_variable_names[var.parents[-1].name]
            + " == "
            + str(domain_index)
            + ":"
        )

    def __generate_assignment__(self, var: BayesVariable, comb: Tuple[str]) -> str:
        assignment = self.polar_variable_names[var.name] + " = "
        for i in range(len(var.domain) - 1):
            assignment += (
                str(i) + " {" + str(var.cpt[comb][i]) + "} "
            )  # var.domain[i] -> i
        return assignment + str(len(var.domain) - 1)

    def __topological_sort__(
        self, variables: List[BayesVariable]
    ) -> List[BayesVariable]:
        num_parents: List[int] = [v.num_parents for v in variables]
        sources: queue.Queue = queue.Queue()
        topological_sort: List[BayesVariable] = []

        for i in range(len(variables)):
            if num_parents[i] == 0:
                sources.put(variables[i])

        while not sources.empty():
            source = sources.get()
            topological_sort.append(source)
            for i in range(len(variables)):
                if source in variables[i].parents:
                    num_parents[i] = num_parents[i] - 1
                    if num_parents[i] == 0:
                        sources.put(variables[i])

        assert len(topological_sort) == len(num_parents)
        return topological_sort
