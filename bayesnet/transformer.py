from math import nan as NaN
from enum import Enum
from lark import Transformer
from .exceptions import BifFormatException
from typing import List, Tuple
from itertools import product
from functools import reduce
from .bayes_variable import BayesVariable
from .bayes_network import BayesNetwork


class AttributeType(Enum):
    ENTRY = 1
    PROPERTY = 2
    DEFAULT = 3
    TABLE = 4
    DOMAIN = 5


class NetworkTransformer(Transformer):
    """
    Lark transformer which checks the lark parse tree and transforms it
    into our network representation
    """
    cpt_tolerance: float
    network: BayesNetwork

    def __init__(self, cpt_tolerance: int):
        super().__init__()
        self.cpt_tolerance = cpt_tolerance
        self.network = None

    def start(self, args):
        network: BayesNetwork = args[0]
        self.network = network
        variables: List[BayesVariable] = [v for v in args[1:] if isinstance(v, BayesVariable)]
        for v in variables:
            if network.has_variable(v.name):
                raise BifFormatException(f"Variable {v.name} is defined multiple times!")
            network.add_variable(v)
            v.network = network
        cpts = [v for v in args[1:] if not isinstance(v, BayesVariable)]
        for cpt in cpts:
            self.__add_cpt__(network, cpt)
        for v in variables:
            if v.cpt is None:
                raise BifFormatException(f"Variable {v.name} has no CPT!")
        return network

    def network_block(self, args):
        network_name = str(args[0])
        properties = [p for (_, p) in args[1:]]
        return BayesNetwork(network_name, properties, self.cpt_tolerance)

    def variable_block(self, args):
        variable_name = str(args[0])
        domain = [p for (d, p) in args[1:] if d == AttributeType.DOMAIN]
        properties = [p for (d, p) in args[1:] if d == AttributeType.PROPERTY]
        if len(domain) == 0:
            raise BifFormatException(f"Variable {variable_name} has no type definitions.")
        elif len(domain) > 1:
            raise BifFormatException(f"Variable {variable_name} has multiple type definitions.")
        return BayesVariable(variable_name, tuple(domain[0]), properties)

    def type(self, args):
        number_values = int(args[0])
        domain = args[1]
        if len(domain) != len(set(domain)):
            raise BifFormatException("Variable domain contains duplicates.")
        elif number_values != len(domain):
            raise BifFormatException("Defined type domain size does not agree with actual domain size.")
        return AttributeType.DOMAIN, domain

    def probability_block(self, args):
        variable, *parents = args[0]
        return variable, parents, args[1:]

    def value_list(self, args):
        return list(map(str, args))

    def ident_list(self, args):
        return list(map(str, args))

    def float_tuple(self, args):
        return tuple(map(float, args))

    def property(self, args):
        return AttributeType.PROPERTY, str(args[0])

    def default(self, args):
        return AttributeType.DEFAULT, args[0]

    def table(self, args):
        return AttributeType.TABLE, args[0]

    def cpt_entry(self, args):
        condition = tuple(args[0])
        probabilities = args[1]
        return AttributeType.ENTRY, (condition, probabilities)

    def __add_cpt__(self, network: BayesNetwork, cpt):
        name, parent_names, cpt_entries = cpt
        parents: List[BayesVariable] = []

        # check if all variables in the header exists
        if not network.has_variable(name):
            raise BifFormatException(f"Variable {name} has CPT, but is not defined!")
        for parent in parent_names:
            if not network.has_variable(parent):
                raise BifFormatException(f"Variable {parent} is parent of variable {name} but not defined!")
            parents.append(network.variables[parent])

        variable: BayesVariable = network.variables[name]
        if variable.cpt is not None:
            raise BifFormatException(f"Variable {name} has two defined CPTs!")
        variable.parents = tuple(parents)

        # for default and table declarations, only the last one is valid
        default, table, entries = None, None, []
        condition_entries = set()
        for (type, element) in cpt_entries:
            if type == AttributeType.DEFAULT:
                if default is not None:
                    raise BifFormatException(f"CPT of Variable {variable.name} has multiple default-declarations.")
                default = element
            elif type == AttributeType.TABLE:
                if table is not None:
                    raise BifFormatException(f"CPT of Variable {variable.name} has multiple table-declarations.")
                table = element
            elif type == AttributeType.ENTRY:
                condition, _ = element
                if condition in condition_entries:
                    raise BifFormatException(f"CPT of Variable {variable.name} has double entry for {condition}.")
                condition_entries.add(condition)
                entries.append(element)
            else:
                assert False

        # fill cpt with default values or NaN:
        self.__add_default__(variable, default)

        # if there is a table attribute, overwrite default values
        self.__add_table__(variable, table)

        # if there are entries, overwrite table/default values
        for condition, probs in entries:
            self.__add_entry__(variable, condition, probs)

        # make sure no NaN's are left
        if variable.cpt_has_nan():
            raise BifFormatException(f"CPT of variable {name} is not fully specified!")
        return

    def __add_default__(self, variable: BayesVariable, default: Tuple[float] = None):
        if default is None:
            default = tuple([NaN for _ in range(variable.domain_size)])
        elif len(default) != variable.domain_size:
            raise BifFormatException(f"Default entry of variable {variable.name} does not cover all variable values.")
        elif not self.network.cpt_entry_sum_valid(default):
            raise BifFormatException(f"Default entry of variable {variable.name} does not sum up to 1.")
        variable.cpt_init(default)

    # table is list of probabilities, where the probabilities
    # are given s.t. the first column is filled top to bottom,
    # then the 2nd column and so on (in counting order).
    def __add_table__(self, variable: BayesVariable, table: Tuple[float]):
        if table is None:
            return
        cpt_num_rows = reduce(lambda x, y: x*y, [p.domain_size for p in variable.parents], 1)
        if len(table) != variable.domain_size * cpt_num_rows:
            raise BifFormatException(f"Table entry for variable {variable.name} does not cover all CPT rows.")
        parent_domains: List[Tuple[str]] = [p.domain for p in variable.parents]
        for row, condition in enumerate(product(*parent_domains)):
            probs = []
            for i in range(variable.domain_size):
                probs.append(table[row + i*cpt_num_rows])
            if not self.network.cpt_entry_sum_valid(probs):
                raise BifFormatException(f"Entry {condition} of variable {variable.name} does not sum up to 1.")
            variable.cpt_set_entry(condition, tuple(probs))

    def __add_entry__(self, variable: BayesVariable, condition: Tuple[str], probs: Tuple[float]):
        name = variable.name
        if len(condition) != variable.num_parents:
            raise BifFormatException(f"Entry {condition} of variable {name} has invalid condition length.")
        elif len(probs) != variable.domain_size:
            raise BifFormatException(f"Entry {condition} of variable {name} has invalid number of values.")
        elif not self.network.cpt_entry_sum_valid(probs):
            raise BifFormatException(f"Entry {condition} of variable {name} does not sum up to 1.")
        else:
            for idx, clause in enumerate(condition):
                if clause not in variable.parents[idx].domain:
                    raise BifFormatException(
                        f"Entry {condition} of variable {name} has invalid condition value {clause}.")
        variable.cpt_set_entry(condition, probs)
