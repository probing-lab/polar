from functools import cache
from sympy import Abs, Expr, Symbol, lambdify, nroots, nsolve, sqrt as sp_sqrt, summation
import numpy as np
from scipy.optimize import fsolve, bisect


N = Symbol("n", integer=True)
C_0 = 0.5591# this is a constant from the berry-esseen-theorem 

@cache
def _get_Ex(p:float,q1:Expr,q2:Expr):
    return (p*q1+(1-p)*q2).simplify()

@cache
def _get_VarX(p, q1, q2) -> Expr:
    return (p*(q1-_get_Ex(p,q1,q2))**2 + (1-p)*((q2-_get_Ex(p,q1,q2))**2)).simplify()

@cache
def _get_bn_expr(p, q1, q2):
    e1 = p*(Abs(q1-_get_Ex(p,q1,q2))**3) + (1-p)*(Abs(q2-_get_Ex(p,q1,q2))**3)
    nominator = summation(e1, (N,0,N))
    
    e2 = _get_VarX(p, q1, q2)
    denominator = summation(e2, (N,0,N))**(3/2)

    return C_0*nominator/denominator

@cache
def _get_bn_func(p, q1, q2):
    expr = _get_bn_expr(p, q1, q2)
    fast_func = lambdify(N, expr, modules="numpy")
    return fast_func

@cache
def _get_expectation_divided_by_sd_expr(p, q1, q2, initial_expr):
    nominator = summation(_get_Ex(p,q1,q2), (N,0,N)) + initial_expr
    denominator = sp_sqrt(summation(_get_VarX(p,q1,q2), (N,0,N)))
    return nominator/denominator   

@cache
def _get_expectation_divided_by_sd_func(p, q1, q2, initial_expr):
    expr = _get_expectation_divided_by_sd_expr(p, q1, q2, initial_expr)

    fast_func = lambdify(N, expr, modules="math")
    return fast_func

def compute_c_0(n_0, p, q1, q2, initial_expr):
    bn = _get_bn_func(p,q1,q2)(n_0)
    mean_deviation_term = _get_expectation_divided_by_sd_func(p,q1,q2, initial_expr)(float(n_0))

    return bn+mean_deviation_term

def compute_delta_cb(n_0, p, q1, q2, initial_expr):
    val = _get_expectation_divided_by_sd_func(p, q1, q2, initial_expr)(n_0)
    return val

def compute_delta_prime(n_0):
    return 1/n_0

def get_n0_from_c0(p, q1, q2, c0, initial_expr):
    bn_expr = _get_bn_expr(p,q1,q2)
    exp_by_sd_expr = _get_expectation_divided_by_sd_expr(p, q1, q2, initial_expr)

    expr = exp_by_sd_expr+bn_expr-c0
    
    fun = lambdify(N, expr, modules="math")
    res = bisect(fun, 1000, 1e15)
    return res

