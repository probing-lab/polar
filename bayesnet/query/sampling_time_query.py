from typing import List
from bayesnet.bayes_network import BayesNetwork
from bayesnet.bayes_variable import BayesVariable
from bayesnet.exceptions import QueryException
from cli.common import transform_to_after_loop
from .query import Query
from bayesnet.common import get_unique_name


class SamplingTimeQuery(Query):
    target_variable: str
    target_value: str

    def __init__(self, query: str, network: BayesNetwork):
        parts = query.split("=")
        if len(parts) != 2:
            raise QueryException("Illegal Format for Sampling Time Query, use VARIABLE = VALUE")
        self.target_variable, self.target_value = [p.strip() for p in parts]
        if self.target_variable not in network.variables:
            raise QueryException(f"Unknown variable {self.target_variable} in Sampling Time Query")
        if self.target_value not in network.variables[self.target_variable].domain:
            raise QueryException(f"Unknown value {self.target_value} in Sampling Time Query")
        return

    def generate_init_code(self, network, polar_variable_mapping) -> List[str]:
        self.count_name = get_unique_name(polar_variable_mapping.values(), "count")
        self.continue_name = get_unique_name(polar_variable_mapping.values(), "continue")
        return [self.count_name + " = 1", self.continue_name + " = 1"]

    def generate_loop_code(self, network, polar_variable_mapping) -> List[str]:
        variable = network.variables[self.target_variable]
        domain_value = variable.domain.index(self.target_value)
        code = [f"\tif {polar_variable_mapping[self.target_variable]} == {domain_value}:"]
        code.append(f"\t\t{self.continue_name} = 0")
        code.append("\tend")
        code.append(f"\t{self.count_name} = {self.count_name} + {self.continue_name}")
        return code

    def generate_query(self, network, polar_variable_mapping):
        return [f"E({self.count_name})"]

    def generate_result(self, results):
        exp_val_count = results[0]
        sampling_time = transform_to_after_loop(exp_val_count)
        print(f"The expected number of samples until {self.target_variable} = {self.target_value} is {sampling_time}")
