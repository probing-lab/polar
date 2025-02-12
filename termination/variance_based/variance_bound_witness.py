from dataclasses import dataclass
from sympy import oo, zeta, log
from termcolor import colored


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
    
    def get_coeff(self, N):
        coeff = (1/self.percentage)**((log(self.n0, self.k+self.epsilon))+1) # TODO: This might be wrong for N>1, should involve some power
        return coeff

    def get_exp_stopping_time_bound(self, N):
        # Computes a bound for E(T^N)
        assert N >= 1, "Exponent for stopping time smaller 1 does not make sense"
        if self.exponent > -1.00000001*N:
            return oo
        
        series_sum = zeta(-self.exponent/N)
        return series_sum*self.get_coeff(N)

    def print(self):
        if(self.terminates):
            print(colored("Program shown to be terminating!", "green"))
        print(f"P(T>t) <= min(1, C * n**({self.exponent})\n")
        print(f"where C={self.get_coeff(1)}\n")
        print(f"E(T)< {self.get_exp_stopping_time_bound(1)}")
        print(f"E(T^N) < oo when "+colored(f"N<={-self.exponent/1.00000001}\n","green"))

