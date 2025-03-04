
from itertools import pairwise
from math import exp, log, sqrt
import sys
from typing import List
import numpy as np
from ortools.linear_solver import pywraplp
from scipy.stats import norm
from heapq import heapify, heappush

from termination.variance_based.exponent_approximation.closed_form_bound import get_closed_form_bound_asymptotic

class PrecisionException(Exception):
    pass

SOLVER_NAME = "GUROBI" # TODO: Should be a command line argument
SCALING = 1 # TODO: This is not so important for gurobi, but might make a difference for other solvers
CUTOFF_MAX_PRECISION = 10e-10

if SOLVER_NAME=="GUROBI": # TODO: this seems messy - but gurobipy seems to be required. I however dislike very much to have gurobipy as a dependency of polar in general.
    import gurobipy
    print(gurobipy.gurobi.version())


def _get_solution(values: List[float], epsilon: float, var_scaling: float, sub_gaussian_cutoff: float, C, delta_2, c0, b):
    # Create the linear solver with the GLOP backend.
    solver = pywraplp.Solver.CreateSolver(SOLVER_NAME) # CLP seems to have better numeric stability (e.g. not so often "ABNORMAL" result) than GLOP
    solver.SetSolverSpecificParametersAsString("OutputFlag=0")

    infinity = solver.infinity()

    exponent = -(sub_gaussian_cutoff - b - delta_2*(sqrt(1+var_scaling)/(sqrt(1+var_scaling)-1)))**2/2
    tail_bound = exp(C*exponent)
    if tail_bound < CUTOFF_MAX_PRECISION:
        raise PrecisionException()
    rem_prob = (1- tail_bound)-epsilon
    rem_prob=rem_prob*SCALING
    print(rem_prob)
    if not solver:
        print(f"Could not create solver {SOLVER_NAME}")
        
    

    cdf_vars =  [solver.NumVar(0,SCALING, f"q_{v}") for v in values]
    pdf_vars = [solver.NumVar(0,SCALING, f"p_{v}") for v in values]
    constraint = solver.Constraint(-infinity,(-epsilon*SCALING), f"p_q_translation_leftmost")
    constraint.SetCoefficient(cdf_vars[0],-1)
    constraint.SetCoefficient(pdf_vars[0],(1-epsilon))        

    for (l_pdf, l_cdf),(r_pdf, r_cdf) in pairwise(zip(pdf_vars, cdf_vars)):
        constraint = solver.Constraint(-infinity,0, f"p_q_translation_{r_pdf}")
        constraint.SetCoefficient(r_pdf,(1-epsilon))
        constraint.SetCoefficient(l_cdf,1)
        constraint.SetCoefficient(r_cdf,-1)

    # For the chernoff bound
    d_cuttoff = solver.NumVar(0,SCALING, "p_chernoff")
    constraint = solver.Constraint(0,rem_prob, "d_cutoff_constraint")
    constraint.SetCoefficient(d_cuttoff, (1-epsilon))
    constraint.SetCoefficient(cdf_vars[-1], (1-epsilon))

    pdf_vars.append(d_cuttoff)
    values.append(sub_gaussian_cutoff)
    

    for idx, value in enumerate(values):
        if idx >= len(cdf_vars):
            continue
        constraint = solver.Constraint(0 , infinity, f"ct_{value}")
        constraint.SetCoefficient(cdf_vars[idx],-SCALING)

        for iv, value1 in enumerate(values):
            z_value = (value*sqrt(1+var_scaling)-value1)/sqrt(var_scaling)
            prob = norm.cdf(z_value)-c0

            constraint.SetCoefficient(pdf_vars[iv], prob*SCALING)

    constraint = solver.Constraint(epsilon*SCALING,SCALING, f"cutoff_larger_epsilon")
    constraint.SetCoefficient(cdf_vars[0], 1)

    objective = solver.Objective()
    objective.SetCoefficient(cdf_vars[0], 1)
    objective.SetMaximization()
    result_status = solver.Solve()
    if result_status == pywraplp.Solver.OPTIMAL:
        return ([var.solution_value()/SCALING for var in cdf_vars])

def _check_if_model_exists(d: float, epsilon:float, C: float, delta_2: float, c_0: float, granularity: int = 201):
    assert 0<epsilon and epsilon < 1

    # deviation of the tail bound from the mean
    b = sqrt(2*log(1/(1-epsilon)))/(C*(sqrt(1+d) - 1))

    for specification_end in np.linspace(3, 16, 13*5+1):
        try:
            for sg_cutoff in np.linspace(2,8,7):
                res = _get_solution(list(np.linspace(0, specification_end, granularity)), epsilon, d, specification_end+sg_cutoff, C, delta_2, c_0, b)
                if res is not None:
                    return (d, epsilon, C, delta_2, c_0, granularity, specification_end, specification_end+sg_cutoff, res)
        except PrecisionException as ex:
            pass # higher sg_cutoff values will have even smaller precision

def estimate_bound_exponent_inductive_bound(degree: float, C: float, delta_1: float, delta_2: float, c_0: float, n_0, granularity: int = 51, num_random_choices = 20, num_steps=8, seed=None):
    """Create an upper bound for the exponent m of the bound $P(T\\geq t) \\leq Bn^{m}$. This method leverages a linear solver to do so.

    Args:
        degree (float): degree of the variance (of the summation)
        epsilon (float): the weight of the distribution that is cut away. Between 0 and 1.
        C (float): factor in the exponent of the tail-bound
        delta_1 (float): multiplicative error for k^{degree}
        delta_2 (float): error for the tail-bound offset
        c_0 (float): maximum absolute deviation from the standard normal cdf
        granularity (int, optional): the granularity of the model for the linear solver. High impact on running time (at least quadratic for model creation and model size). Defaults to 401.
    """
    # Monte-Carlo-Algorithm - there is no guarantee to find an exponent that is optimal in some sense (soundness is given though).

    # we want to minimize log(1-pterm)/log(k*delta_1)
    # simultaniously, d = k**degree


     # TODO: this does not respect constants at all. Therefore add the divide by 2.
    priority_queue = [(get_closed_form_bound_asymptotic(degree, C), None)]
    random_generator = np.random.default_rng(seed)

    for i in range(num_random_choices):
        epsilon = random_generator.random()*0.4
        prev_min_exponent = priority_queue[0][0]
        print(f"Epsilon: {epsilon}")

        # required d to be new good candidate
        k_req =  exp((1.4*log(1-epsilon)/prev_min_exponent)) - delta_1
        d_current = k_req**degree-1
        d_min = d_current
        res_min = None
        
        res_min =  _check_if_model_exists(d_current, epsilon, C, delta_2, c_0, granularity)
        if res_min == None:
            print(f"Skipping epsilon: {epsilon}")

            continue # Bad guess - nothing was found

        # binary search over d_current
        d_stepsize = d_current/2
        d_current = d_current/2

        for _ in range(num_steps):
            
            res = _check_if_model_exists(d_current, epsilon, C, delta_2, c_0, granularity)
            d_stepsize = d_stepsize/2

            if res is not None:
                res_min = res
                d_min = d_current
                d_current = d_current - d_stepsize
            else:
                d_current = d_current + d_stepsize
        
        k = (d_min+1)**(1/degree)+delta_1
        exponent = log(1-epsilon)/log(k)
        print(f"New min exponent for epsilon: {epsilon}: {exponent}")

        heappush(priority_queue, (exponent, res_min))
            

    print(priority_queue)
