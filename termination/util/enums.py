from enum import Enum


class LogicalState(Enum):
    Unsat = 1
    Sat = 2
    Valid = 3


class TerminationProperty(Enum):
    Terminating = 1
    Nontermination = 2
