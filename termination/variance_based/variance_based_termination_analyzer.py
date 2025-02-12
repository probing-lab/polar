# This file follows the draft "Verifying Positive Almost-Sure Termination using Variance"

from math import exp, log, sqrt
import math
import sys
from sympy import S, Abs, Poly, Symbol, nroots, nsolve, summation, sqrt as sp_sqrt
from scipy.stats import norm
import numpy as np

from termination.variance_based.variance_bound_witness import VarianceBoundWitness

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
    
    def _estimate_bound_percentage_of_terminating(self,m, C, delta1, delta2, epsilon, c_0, n_0):
        # TODO: This numeric approximation is very naive
        k_min = None
        perc_min = None
        t_min = None
        exp_min = 0
        for k in np.linspace(math.pow(6.87, 1/(2*m+1)), 20, 1000):
            for t in np.linspace(2,30, 100):
                perc = 1-self._calculate_percentage_of_terminating(t,math.pow(k,(2*m+1)),C,delta1,delta2,c_0)
                exp = log(perc)/log(k+epsilon)
                if perc >= 0.999:
                    continue
                if exp < exp_min:
                    t_min = t
                    perc_min = perc
                    k_min = k
                    exp_min = exp

        return VarianceBoundWitness(epsilon, delta1, delta2, m, t_min, k_min, exp_min, perc_min, n_0)

    def _estimate_needed_exponent(self,C, delta1, delta2, c_0):#
        # This function computes the minimum exponent, rather than computing the bound when given an exponent
        k_min = None
        perc_min = None
        m_min = sys.maxsize
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
        return exponent_min
    
    def _n_zero_delta1(self, delta1, q_var):
        # Maybe we must skip this for large polys
        # the delta1 we use is actually smaller than the delta1 provided 
        # TODO: the larger error should be "granted" to the side corresponding to the sign of the second highes coeff.
        # TODO: Currently this is done very naively
        var_ltmonom, var_ltcoeff = q_var.LT()
        q_bound = (q_var - var_ltmonom.as_expr()*var_ltcoeff).simplify()

        if q_bound.is_zero:
            return 0
        
        _, second_coeff = q_bound.LT()
        if second_coeff < 0:
            a,b = 1, 20
        else:
            a,b = 20, 1

        delta_bound = (1-delta1)/(a+delta1*b)


        # lower bound
        leading_monom = var_ltmonom.as_expr()*var_ltcoeff
        poly1 = q_bound - leading_monom*delta_bound*a
        # if all coeffs are negative, then there will be no root
        if all(c < 0 for c in poly1.all_coeffs()):
            r1 = 0
        # Check if all coefficients are negative
        else:
            roots1 = [r for r in nroots(poly1, maxsteps=100) if r.is_real]
            if len(roots1) == 0:
                r1 = 0
            else:
                r1 = roots1[-1]
        # upper bound
        poly2 = q_bound + leading_monom*delta_bound*b
        # if all coeffs are negative, then there will be no root
        if all(c > 0 for c in poly2.all_coeffs()):
            r2 = 0
        # Check if all coefficients are negative
        else:
            roots2 = [r for r in nroots(poly2, maxsteps=100) if r.is_real]
            if len(roots2) == 0:
                r2 = 0
            else:
                r2 = roots2[-1]
        return max(r1, r2)
    
    def _n_zero_delta2(self, delta2, q_var, q_exp):
        poly1 = q_exp-q_var*delta2
        roots = [r for r in nroots(poly1, maxsteps=100) if r.is_real]
        if len(roots)==0:
            return 0
        return roots[-1]

    def _n_zero_c_0(self, c0, q_var, q_c3, q_exp):
        # TODO: This solve may still be a bis sketchy - especially the initial quess.
        C0 = 20

        expr = C0*q_c3.as_expr()/sp_sqrt(q_var.as_expr()**3)
        expr1 = q_exp.as_expr()/sp_sqrt(q_var.as_expr())

        root = nsolve(expr+expr1-c0,N, 10000, maxsteps=100000, tol=1e-10)
        return root


    def compute_bound(self, delta1, delta2, c_0, epsilon=None):
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
        assert max_degree_q1 == max_degree_q2 and max_coeff_p1*self.p1+max_coeff_p2*self.p2 == S.Zero,"Degree of expected value of loop guard change not lower than twice the degree of the variance."


        q_exp_indiv = q1*self.p1+q2*self.p2
        q_exp = summation((q1*self.p1+q2*self.p2).as_expr(),(N, 1, N))
        q_exp = Poly(q_exp, N)

        q_var_inidiv = ((q1-q_exp_indiv)**2*self.p1+(q2-q_exp_indiv)**2*self.p2).simplify()
        q_var = summation(q_var_inidiv.as_expr(), (N, 1, N))
        q_var = Poly(q_var)

        # for large exponent, skip n_0 computation. We know it exists and is finite, but computing is time consuming
        if max_degree_q1 > 10:
            n_0 = Symbol("n_0")
        else:
            n_0_delta1 = self._n_zero_delta1(delta1, q_var)

            n_0_delta2 = self._n_zero_delta2(delta2, q_var, q_exp)

            # 3rd central moment
            q_c3 = ((Abs((q1-q_exp_indiv).as_expr()))**3*self.p1+(Abs((q2-q_exp_indiv).as_expr()))**3*self.p2).simplify()
            q_c3 = summation(q_var_inidiv.as_expr(), (N, 1, N))

            n_0_c_0 = self._n_zero_c_0(c_0, q_c3, q_var, q_exp)

            n_0 = max(n_0_delta1, n_0_delta2, n_0_c_0)

        if epsilon==None:
            # compute it from n_0
            epsilon = 0.001

        witness = self._estimate_bound_percentage_of_terminating(max_degree_q1, C, delta1, delta2, epsilon, c_0, n_0)
        # For the percentage we have two parameters: t>1 and k, such that k**m >= 6.86546


        return witness