# This file follows the draft "Verifying Positive Almost-Sure Termination using Variance"

from math import exp, log, sqrt
from sympy import S, Poly, Symbol
from scipy.stats import norm
import numpy as np

N = Symbol("n", integer=True)

class VarianceBasedTerminationAnalyzer:
    def  __init__(self, p1, q1, p2, q2):
        self.p1 = p1
        self.q1 = q1
        self.p2 = p2
        self.q2 = q2
        assert q1.free_symbols == set([N]), "Only 'n' may occur in polynomial q1"
        assert q2.free_symbols == set([N]), "Only 'n' may occur in polynomial q2"


    def _calculate_percentage_of_terminating(self, t, d, C, delta1, delta2, c_0):
        left_lower_bound = (1-exp(C*(-(t-1-delta2)**2)/(2*(d*delta1/(d*delta1-1))**2))) 
        left_lower_bound2 = (norm.cdf(-(t)/sqrt(d*delta1-1))-c_0)
        union_bound = left_lower_bound*left_lower_bound2
        return union_bound

    def _estimate_bound_percentage_of_terminating(self,m, C, delta1, delta2, c_0):
        k_min = None
        perc_min = None
        m_min = 10000000000000
        t_min = None
        d_min = None
        for d in np.linspace(6.87, 10000, 10000):
            for t in np.linspace(2,50, 100):
                perc = 1-self._calculate_percentage_of_terminating(t,d,C,delta1,delta2,c_0)
                if perc >= 0.999:
                    continue
                k_upper_bound = 1/perc
                required_m = (log(d+1)/log(k_upper_bound) - 1)/2
                if m_min > required_m:
                    t_min = t
                    d_min = d
                    m_min=required_m
                    perc_min = perc
                    k_min = k_upper_bound

        exponent_min = log(perc_min)/log(k_min)
        pass

    def compute_bound(self, delta1, delta2, c_0):
        # we need to compute (n'_0(delta1,delta2,c_0)) and then 
        # approximate the percentage of terminating.
        q1 = Poly(self.q1)
        q2 = Poly(self.q2)
        C = 4*(self.p1*self.p2)


        max_degree_q1, max_coeff_p1 =  q1.LT()
        max_degree_q1 = max_degree_q1.exponents[0]

        max_degree_q2, max_coeff_p2 =  q2.LT()
        max_degree_q2 = max_degree_q2.exponents[0]

        # This verifies, that deg(E(X_i)) < deg(Var(X_i))/2
        assert max_degree_q1 == max_degree_q2 and max_coeff_p1+max_coeff_p2 == S.Zero,"Degree of expected value of loop guard change not lower than twice the degree of the variance."

        res = self._estimate_bound_percentage_of_terminating(max_degree_q1, C, delta1, delta2, c_0)
        # For the percentage we have two parameters: t>1 and k, such that k**m >= 6.86546
        pass