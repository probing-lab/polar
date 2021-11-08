from bayes_variable import BayesVariable
from typing import List, Dict


class BayesNetwork:
    name: str
    properties: List[str]
    variables: Dict[str, BayesVariable]

    def __init__(self, name: str, properties: List[str] = []):
        self.name = name
        self.properties = properties
        self.variables = {}

    def add_variable(self, bayes_var: BayesVariable) -> None:
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
