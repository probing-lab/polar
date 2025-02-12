from dataclasses import dataclass
from math import log
from sympy import oo, zeta


@dataclass
class VarianceBoundWitness:
    # Parameters
    epsilon: float
    delta1: float
    delta2: float
    m: float|int

    # computed
    t: float
    k: float
    exponent: float
    percentage: float

    n0: float

    def terminates(self):
        return self.exponent < -1.00000001 # To ensure actual smaller, preventing floating point errors, as non-equality is needed.
    
    def get_exp_stopping_time_bound(self, N):
        # Computes a bound for E(T^N)
        assert N >= 1, "Exponent for stopping time smaller 1 does not make sense"
        if self.exponent > -1.00000001*N:
            return oo
        
        series_sum = zeta(-self.exponent/N)
        coeff = (1/self.percentage)**((log(self.n0, self.k+self.epsilon))+1)
        return series_sum*coeff

    def __str__(self):
        pass
