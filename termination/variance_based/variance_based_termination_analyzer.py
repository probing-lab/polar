# This file follows the draft "Verifying Positive Almost-Sure Termination using Variance"

from math import exp, log, sqrt
import math
import sys
from sympy import S, Abs, Poly, Symbol, nroots, nsolve, summation, sqrt as sp_sqrt
from scipy.stats import norm
import numpy as np
from termination.variance_based.exponent_approximation.genetic_algorithm import estimate_bound_exponent_inductive_bound_genetic
from termination.variance_based.exponent_approximation.genetic_algorithm_config import MinMaxQuadraticAlgorithmConfig
from termination.variance_based.exponent_approximation.inductive_bound import estimate_bound_exponent_inductive_bound

from termination.variance_based.variance_bound_witness import VarianceBoundWitness

N = Symbol("n", integer=True)

class VarianceBasedTerminationAnalyzer:
    def  __init__(self, p1, q1, p2, q2, initial_value):
        self.p1 = p1
        self.q1 = q1
        self.p2 = p2
        self.q2 = q2
        self.initial_value = initial_value
        assert q1.free_symbols ==set() or q1.free_symbols == set([N]), "Only 'n' may occur in polynomial q1"
        assert q1.free_symbols ==set() or q2.free_symbols == set([N]), "Only 'n' may occur in polynomial q2"

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


    def compute_bound(self, exact):
        # we need to compute (n'_0(delta1,delta2,c_0)) and then 
        # approximate the percentage of terminating.
        q1 = Poly(self.q1, gens = [N])
        q2 = Poly(self.q2, gens = [N])
        max_degree_q1, max_coeff_p1 =  q1.LT()
        max_degree_q1 = max_degree_q1.exponents[0]

        max_degree_q2, max_coeff_p2 =  q2.LT()
        max_degree_q2 = max_degree_q2.exponents[0]
        # This verifies, that deg(E(X_i)) < deg(Var(X_i))/2
        assert max_degree_q1 == max_degree_q2 and max_coeff_p1*self.p1+max_coeff_p2*self.p2 == S.Zero,"Degree of expected value of loop guard change not lower than twice the degree of the variance."

        witness = estimate_bound_exponent_inductive_bound_genetic(max_degree_q1*2+1, self.p1,MinMaxQuadraticAlgorithmConfig(20, 20, 400, 10, 100, 10, degree_pop=0.5), q1, q2,initial_expr=self.initial_value, exact_n0=exact)
        # For the percentage we have two parameters: t>1 and k, such that k**m >= 6.86546


        return witness