from dataclasses import dataclass
from typing import Optional
from sympy import Expr, oo
from termcolor import colored
from scipy.special import zeta
import numpy as np


@dataclass
class VarianceBoundWitness:
    """The we compute is actually for "P(T >= n)", and has the form Bn^m."""

    # Parameters
    m: float
    B: (
        float | Expr
    )  # this either is a number, or it can be a (known to be finite) expression
    n0: Optional[float]

    def terminates(self):
        return (
            self.m < -1.00000001
        )  # To ensure actual smaller, preventing floating point errors, as non-equality is needed.

    def get_exp_stopping_time_bound(self, N):
        # Computes a bound for E(T^N)
        assert N >= 1, "Exponent for stopping time smaller 1 does not make sense"
        if self.m > -1.00000001 * N:
            return oo
        if self.n0:
            return self.B**N * (zeta(-self.m / N, self.n0 + 1)) + self.n0**N
        else:
            return self.B**N * (zeta(-self.m / N))

    def print(self):
        if self.terminates():
            print(colored("Program shown to be terminating!", "green"))
        else:
            print(colored("Program termination could not be shown", "red"))
        print(f"P(T>t) <= min(1, B * n**({self.m})\n")
        print(f"where B={self.B}\n")
        print(f"E(T)< {self.get_exp_stopping_time_bound(1)}")
        print(f"E(T^N) < oo when " + colored(f"N<={-self.m/1.00000001}\n", "green"))
