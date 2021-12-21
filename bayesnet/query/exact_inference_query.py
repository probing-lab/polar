from typing import List, Tuple
from bayesnet.bayes_network import BayesNetwork
from bayesnet.bayes_variable import BayesVariable
from bayesnet.exceptions import QueryException
from cli.common import transform_to_after_loop
from .query import Query
from bayesnet.common import get_unique_name


class ExactInferenceQuery(Query):
    target_variable: str
    target_power: str
    evidence: List[Tuple[str, str]]
    indicator_name: str
    inference_name: str
    query: str
    network: BayesNetwork

    def __init__(self, query: str, network: BayesNetwork):
        self.query = query
        self.network = network
        self.evidence = []
        parts = query.split("|")
        if len(parts) != 2:
            raise QueryException("Illegal Format for Exact Inference Query, use VAR**k | VAR = VAL, VAR = VAL, ..")
        target_expr = parts[0].strip().split("**")
        self.target_variable = target_expr[0]
        if len(target_expr) == 1:
            self.target_power = 1
        elif len(target_expr) == 2:
            self.target_power = int(target_expr[1])
        else:
            raise QueryException(f"Invalid query {parts[0].strip()} in Exact Inference Query")

        if self.target_variable not in network.variables:
            raise QueryException(f"Unknown variable {self.target_variable} in Exact Inference Query")

        # process evidence
        evidence_list = [p.strip() for p in parts[1].split(",")]
        for evidence_assignment in evidence_list:
            evidence_parts = evidence_assignment.split("=")
            if len(evidence_parts) != 2:
                raise QueryException("Illegal Format for Exact Inference Query, use VAR**k | VAR = VAL, VAR = VAL, ..")
            evidence_var, evidence_value = [p.strip() for p in evidence_parts]
            if evidence_var not in network.variables:
                raise QueryException(f"Unknown variable {evidence_var} in Exact Inference Query")
            if evidence_value not in network.variables[evidence_var].domain:
                raise QueryException(f"Unknown value {evidence_value} in Exact Inference Query")
            self.evidence.append((evidence_var, evidence_value))
        return

    def generate_init_code(self, network, polar_variable_mapping) -> List[str]:
        target_var_polar_name = polar_variable_mapping[self.target_variable]
        self.indicator_name = get_unique_name(polar_variable_mapping.values(), "ind_" + target_var_polar_name)
        self.inference_name = get_unique_name(polar_variable_mapping.values(), "inf_" + target_var_polar_name)
        return [self.indicator_name + " = 0", self.inference_name + " = 0"]

    def generate_loop_code(self, network, polar_variable_mapping) -> List[str]:
        condition = "\tif "
        for i in range(len(self.evidence) - 1):
            ev_var, ev_val = self.evidence[i]
            variable = network.variables[ev_var]
            domain_value = variable.domain.index(ev_val)
            condition += polar_variable_mapping[ev_var] + " == " + str(domain_value) + " && "

        ev_var, ev_val = self.evidence[-1]
        variable = network.variables[ev_var]
        domain_value = variable.domain.index(ev_val)
        condition += polar_variable_mapping[ev_var] + " == " + str(domain_value) + ":"

        code = [condition]
        code.append(f"\t\t{self.indicator_name} = 1")
        code.append("\telse:")
        code.append(f"\t\t{self.indicator_name} = 0")
        code.append("\tend")

        code.append(f"\t{self.inference_name} = {polar_variable_mapping[self.target_variable]} * {self.indicator_name}")
        return code

    def generate_query(self, network, polar_variable_mapping):
        return [f"E({self.inference_name}**{self.target_power})", f"E({self.indicator_name})"]

    def generate_result(self, results):
        exp_val_inference = results[0]
        exp_val_indicator = results[1]
        result = transform_to_after_loop(exp_val_inference / exp_val_indicator)
        print(f"E({self.query}) = {result} ≈ {result.evalf(10)}")
        print(f"\tThe domain of '{self.target_variable}' has been mapped as follows:")
        for index, domain_element in enumerate(self.network.variables[self.target_variable].domain):
            print(f"\t{index} <-> {domain_element}")
