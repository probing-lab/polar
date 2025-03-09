from functools import cache
from sympy import Abs, Expr, Symbol, lambdify, sqrt as sp_sqrt, summation
import numpy as np


N = Symbol("n", integer=True)
C_0 = 0.5591# this is a constant from the berry-esseen-theorem 

@cache
def _get_Ex(p:float,q1:Expr,q2:Expr):
    return (p*q1+(1-p)*q2).simplify()

@cache
def _get_VarX(p, q1, q2) -> Expr:
    return (p*(q1-_get_Ex(p,q1,q2))**2 + (1-p)*((q2-_get_Ex(p,q1,q2))**2)).simplify()

@cache
def _get_bn_func(p, q1, q2):
    e1 = p*(Abs(q1-_get_Ex(p,q1,q2))**3) + (1-p)*(Abs(q2-_get_Ex(p,q1,q2))**3)
    nominator = summation(e1, (N,0,N))
    
    e2 = _get_VarX(p, q1, q2)
    denominator = summation(e2, (N,0,N))**(3/2)

    expr = C_0*nominator/denominator

    fast_func = lambdify(N, expr, modules="numpy")
    return fast_func

@cache
def _get_expectation_divided_by_sd_func(p, q1, q2):
    nominator = summation(_get_Ex(p,q1,q2), (N,0,N))
    denominator = sp_sqrt(summation(_get_VarX(p,q1,q2), (N,0,N)))
    expr = nominator/denominator

    fast_func = lambdify(N, expr, modules="math")
    return fast_func

def compute_c_0(n_0, p, q1, q2):
    bn = _get_bn_func(p,q1,q2)(n_0)
    mean_deviation_term = _get_expectation_divided_by_sd_func(p,q1,q2)(float(n_0))

    return bn+mean_deviation_term

def compute_delta_cb(n_0, p, q1, q2):
    val = _get_expectation_divided_by_sd_func(p, q1, q2)(n_0)
    return val

def compute_delta_prime(n_0):
    return 1/n_0
