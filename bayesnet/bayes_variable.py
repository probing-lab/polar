from __future__ import annotations
from math import nan as NaN
from typing import List, Tuple, Dict
from itertools import product

import bayes_network


class BayesVariable:
    name: str
    domain: Tuple[str]
    properties: List[str]
    parents: Tuple[BayesVariable]
    network: bayes_network.BayesNetwork
    cpt: Dict[Tuple[str], Tuple[float]]

    def __init__(self, name: str, domain: Tuple[str], properties: List[str]):
        self.name = name
        self.domain = domain
        self.properties = properties
        self.parents = None
        self.cpt = None

    @property
    def domain_size(self):
        return len(self.domain)

    @property
    def num_parents(self):
        return len(self.parents)

    def print_pretty(self, indent: int = 0) -> str:
        indent = " " * indent
        pretty: str = indent + str(self) + "\n"
        parent_domains: List[Tuple[str]] = [p.domain for p in self.parents]
        for comb in product(*parent_domains):
            pretty += indent + "  " + f"{comb}: {self.cpt[comb]}\n"
        return pretty

    def cpt_init(self, entry: Tuple[float]):
        assert len(entry) == self.domain_size
        if NaN not in entry:
            assert self.network.cpt_entry_sum_valid(entry)
        self.cpt = {}
        parent_domains: List[Tuple[str]] = [p.domain for p in self.parents]
        for comb in product(*parent_domains):
            self.cpt[comb] = entry

    def cpt_set_entry(self, condition: Tuple[str], probabilities: Tuple[float]):
        assert len(probabilities) == self.domain_size
        assert len(condition) == self.num_parents
        assert self.network.cpt_entry_sum_valid(probabilities)
        for idx, val in enumerate(condition):
            assert val in self.parents[idx].domain
        self.cpt[condition] = probabilities

    def cpt_has_nan(self) -> bool:
        parent_domains: List[Tuple[str]] = [p.domain for p in self.parents]
        for comb in product(*parent_domains):
            if NaN in self.cpt[comb]:
                return True

    def __str__(self) -> str:
        return f"Variable '{self.name}', Domain: {str(self.domain)}, Properties: {str(self.properties)}"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            result = True
            result = result and (self.name == other.name)
            result = result and (self.domain == other.domain)
            result = result and (self.parents == other.parents)
            result = result and (self.properties == other.properties)
            result = result and (self.cpt == other.cpt)
            return result
        else:
            return False
