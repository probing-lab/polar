from typing import List, Tuple
from bayesnet.bayes_network import BayesNetwork
from bayesnet.bayes_variable import BayesVariable
from bayesnet.exceptions import QueryException
from .query import Query
from bayesnet.common import get_unique_name


class ExactInferenceQuery(Query):
    target_variable: str
    evidence: List[Tuple[str, str]]
    indicator_name: str
    inference_name: str

    def __init__(self, query: str, network: BayesNetwork):
        self.evidence = []
        parts = query.split("|")
        if len(parts) != 2:
            raise QueryException("Illegal Format for Exact Inference Query, use VAR | VAR = VAL, VAR = VAL, ..")
        self.target_variable = parts[0].strip()
        if self.target_variable not in network.variables:
            raise QueryException(f"Unknown variable {self.target_variable} in Exact Inference Query")

        # process evidence
        evidence_list = [p.strip() for p in parts[1].split(",")]
        for evidence_assignment in evidence_list:
            evidence_parts = evidence_assignment.split("=")
            if len(evidence_parts) != 2:
                raise QueryException("Illegal Format for Exact Inference Query, use VAR | VAR = VAL, VAR = VAL, ..")
            evidence_var, evidence_value = [p.strip() for p in evidence_parts]
            if evidence_var not in network.variables:
                raise QueryException(f"Unknown variable {evidence_var} in Exact Inference Query")
            if evidence_value not in network.variables[evidence_var].domain:
                raise QueryException(f"Unknown value {evidence_value} in Exact Inference Query")
            self.evidence.append((evidence_var, evidence_value))
        return

    def generate_init_code(self, network, polar_variable_mapping) -> List[str]:
        self.indicator_name = get_unique_name(polar_variable_mapping.values(), "ind_" + self.target_variable)
        self.inference_name = get_unique_name(polar_variable_mapping.values(), "inf_" + self.target_variable)
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
        return [f"E({self.inference_name})", f"E({self.indicator_name})"]
