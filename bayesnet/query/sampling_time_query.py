from threading import Condition
from typing import List

from sympy.core.symbol import var
from bayesnet.bayes_network import BayesNetwork
from bayesnet.bayes_variable import BayesVariable
from bayesnet.exceptions import QueryException
from cli.common import transform_to_after_loop
from .query import Query
from bayesnet.common import get_unique_name

# so far only conjunctions are supported
# format: VARIABLE = VALUE, VARIABLE = VALUE, ...


class SamplingTimeQuery(Query):
    target_variables: List[str]
    target_values: List[str]
    query: str

    def __init__(self, query: str, network: BayesNetwork):
        self.query = query
        self.target_values = []
        self.target_variables = []

        conditions = [q.strip() for q in query.split(",")]
        for condition in conditions:
            condition_parts = condition.split("=")
            if len(condition_parts) != 2:
                raise QueryException("Illegal Format for Sampling Time Query, use VAR = VAL, VAR = VAL, ..")
            cond_var, cond_val = [p.strip() for p in condition_parts]
            if cond_var not in network.variables:
                raise QueryException(f"Unknown variable {cond_var} in Sampling Time Query")
            if cond_val not in network.variables[cond_var].domain:
                raise QueryException(f"Unknown value {cond_val} in Sampling Time Query")
            self.target_variables.append(cond_var)
            self.target_values.append(cond_val)
        return

    def generate_init_code(self, network, polar_variable_mapping) -> List[str]:
        self.count_name = get_unique_name(polar_variable_mapping.values(), "count")
        self.continue_name = get_unique_name(polar_variable_mapping.values(), "continue")
        return [self.count_name + " = 1", self.continue_name + " = 1"]

    def generate_loop_code(self, network, polar_variable_mapping) -> List[str]:
        condition = "\tif "
        for i in range(len(self.target_variables) - 1):
            variable_name = self.target_variables[i]
            variable = network.variables[variable_name]
            domain_value = variable.domain.index(self.target_values[i])
            condition += polar_variable_mapping[variable_name] + " == " + str(domain_value) + " && "

        variable_name = self.target_variables[-1]
        variable = network.variables[variable_name]
        domain_value = variable.domain.index(self.target_values[-1])
        condition += polar_variable_mapping[variable_name] + " == " + str(domain_value) + ":"

        code = [condition]
        code.append(f"\t\t{self.continue_name} = 0")
        code.append("\tend")
        code.append(f"\t{self.count_name} = {self.count_name} + {self.continue_name}")
        return code

    def generate_query(self, network, polar_variable_mapping):
        return [f"E({self.count_name})"]

    def generate_result(self, results):
        exp_val_count = results[0]
        sampling_time = transform_to_after_loop(exp_val_count)
        print(f"The expected number of samples until {self.query} is {sampling_time} ≈ {sampling_time.evalf(10)}")
