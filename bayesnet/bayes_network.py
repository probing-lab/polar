from __future__ import annotations
import bayes_variable
from typing import List, Dict, Tuple


class BayesNetwork:
    name: str
    properties: List[str]
    variables: Dict[str, bayes_variable.BayesVariable]
    cpt_tolerance: float

    def __init__(self, name: str, properties: List[str], cpt_tolerance: float):
        self.name = name
        self.properties = properties
        self.variables = {}
        self.cpt_tolerance = cpt_tolerance

    def add_variable(self, bayes_var: bayes_variable.BayesVariable) -> None:
        assert not self.has_variable(bayes_var.name)
        self.variables[bayes_var.name] = bayes_var
        return

    def has_variable(self, name: str) -> bool:
        return (self.variables.get(name) is not None)

    def print_pretty(self, indent: int = 0) -> str:
        pretty: str = (" " * indent) + str(self) + "\n"
        for v in self.variables.values():
            pretty += v.print_pretty(indent + 2)
        return pretty

    def __str__(self) -> str:
        return f"Network '{self.name}', Properties: {str(self.properties)}"

    def cpt_entry_sum_valid(self, probabilities: Tuple[float]) -> bool:
        return abs(1 - sum(probabilities)) < self.cpt_tolerance

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            result = True
            result = result and (self.name == other.name)
            result = result and (self.properties == other.properties)
            result = result and (self.cpt_tolerance == other.cpt_tolerance)
            result = result and (self.variables == other.variables)
            return result
        else:
            return False
