from dataclasses import dataclass
from functools import cache
from math import exp, log
from typing import List
from sympy import Expr

import numpy as np
from termination.polynomial.termination_witness import TerminationWitness
from termination.variance_based.exponent_approximation.bound_validation import validate_bound
from termination.variance_based.exponent_approximation.closed_form_bound import _get_c_d_prime, get_closed_form_bound_asymptotic
from termination.variance_based.exponent_approximation.converging_constants import compute_c_0, compute_delta_cb, compute_delta_prime
from termination.variance_based.exponent_approximation.genetic_algorithm_config import GeneticAlgorithmConfig
from termination.variance_based.exponent_approximation.inductive_bound import PrecisionException, _check_model, _compute_b
from termination.variance_based.variance_bound_witness import VarianceBoundWitness

@dataclass
class InductiveBoundSpecification:
    n0 : float
    d: float
    epsilon: float
    granularity: int
    specification_end: float
    sg_cutoff: float

    def __hash__(self):
        return hash((self.d, self.epsilon, self.granularity, self.specification_end, self.sg_cutoff))
    
    def __eq__(self, value):
        return isinstance(value, self.__class__) and value.d == self.d and value.epsilon == self.epsilon and value.granularity == self.granularity and\
              value.specification_end == self.specification_end and value.sg_cutoff == self.sg_cutoff

class GeneticAlgorithm:
    def __init__(self, C:float, p: float, q1: Expr, q2: Expr, degree:float, seed=None):
        self.C = C
        self.p = p
        self.q1 = q1
        self.q2 = q2
        self.degree = degree
        self.rand_gen = np.random.default_rng(seed)

        self.population: List[InductiveBoundSpecification] = None

    def _get_delta_1(self, n0):
        if self.q1 is None or self.q2 is None:
            return 1e-8
        return compute_delta_cb(n0, self.p, self.q1.as_expr(), self.q2.as_expr())

    def _get_delta_prime(self, n0):
        if self.q1 is None or self.q2 is None:
            return 1e-8
        return compute_delta_prime(n0)
        
    def _get_c_0(self, n0):
        if self.q1 is None or self.q2 is None:
            return 1e-8
        return compute_c_0(n0, self.p, self.q1.as_expr(), self.q2.as_expr())

    @cache
    def fitness(self, spec: InductiveBoundSpecification):
        try:
            c_0 = self._get_c_0(spec.n0)
            delta_1 = self._get_delta_1(spec.n0)
            if _check_model(spec.d, spec.epsilon, self.C, delta_1, c_0, 
                            spec.granularity, spec.specification_end, spec.sg_cutoff, 
                            _compute_b(spec.epsilon, spec.d, self.C)) is not None:
                fitness = -log(1-spec.epsilon)/log((spec.d+1)**(1/self.degree) + self.delta_1) # compute the exponent. times (-1) to have positive fitness
                return fitness
            else:
                return 0
        except PrecisionException as ex:
            return 0
        
    def get_best_bound(self):
        if len(self.population) < 1:
            return None
        spec = self.population[0]
        c_0 = self._get_c_0(self.population[0].n0)
        delta_1 = self._get_delta_1(self.population[0].n0)
        res = _check_model(spec.d, spec.epsilon, self.C, delta_1, c_0, 
                            spec.granularity, spec.specification_end, spec.sg_cutoff, 
                            _compute_b(spec.epsilon, spec.d, self.C))
        res_vals = np.linspace(0, spec.specification_end, spec.granularity)
        return res, res_vals, spec.epsilon, spec.d, spec.specification_end+spec.sg_cutoff
        
    def mutate(self, spec: InductiveBoundSpecification, new_granularity):
        d = spec.d
        epsilon = spec.epsilon
        granularity = new_granularity
        specification_end = spec.specification_end
        sg_cutoff = spec.sg_cutoff
        n0 = spec.n0

        if self.rand_gen.random() < 0.4: # small step
            d *=(self.rand_gen.random()*0.1+0.9)
        elif self.rand_gen.random() < 0.3:
            d *=(self.rand_gen.random()*0.5+0.55)
        if self.rand_gen.random() < 0.4: # small step
            epsilon *= (self.rand_gen.random()*0.08+0.99)
        elif self.rand_gen.random() < 0.2:
            epsilon *= (self.rand_gen.random()*0.3+0.9)
        if self.rand_gen.random() < 0.3:
            specification_end *= (self.rand_gen.random()*0.4 + 0.8)
        if self.rand_gen.random() < 0.3:
            sg_cutoff *= (self.rand_gen.random()*0.4 + 0.8)

        return InductiveBoundSpecification(n0, d, epsilon, granularity, specification_end, sg_cutoff)

    def get_initial_guesses(self, granularity, size):
        exp_asym_bound = get_closed_form_bound_asymptotic(self.degree, self.C)/1.8
        
        self.population=[]
        c_prime, d_prime = _get_c_d_prime(self.C) # this serves just as a heuristic, to always guess in the somewhat right area
        for _ in range(size):
            epsilon = self.rand_gen.random()*0.3+0.1
            n0 = 10000
            delta_1 = self._get_delta_prime(n0)
            k =  exp((log(1-epsilon)/exp_asym_bound)) - delta_1
            d = k**self.degree - 1
            sg_cutoff_total = self.rand_gen.random()*c_prime+5.5
            specification_end = sg_cutoff_total - (self.rand_gen.random()*4.5+1)
            sg_cutoff = sg_cutoff_total-specification_end
            self.population.append(InductiveBoundSpecification(
                n0, d, epsilon, granularity, specification_end, sg_cutoff
            ))

    def get_new_population(self, multipier, new_granularity):
        elems = self.rand_gen.choice(self.population, multipier*len(self.population), replace=True)
        self.population = self.population + [self.mutate(spec, new_granularity) for spec in elems]

    def sort_population(self):
        self.population = sorted(self.population, key=lambda spec: self.fitness(spec), reverse=True)
        
    def shrink_population(self, size):
        self.population = self.population[:size]

    def print_best(self):
        print(f"exponent: {-self.fitness(self.population[0])},epsilon: {self.population[0].epsilon}, d: {self.population[0].d}, spec_end: {self.population[0].specification_end}, sg_cutoff: {self.population[0].sg_cutoff}")


def estimate_bound_exponent_inductive_bound_genetic(degree: float, p:float, algorithm_config: GeneticAlgorithmConfig, q_1: Expr, q_2: Expr, exact_n0=False, seed=0):
    """Create an upper bound for the exponent m of the bound $P(T\\geq t) \\leq Bn^{m}$. This method leverages a linear solver to do so.
    """
    assert 0 < p and p<1, "p must be a valid percentage between ]0;1["
    C = 4*p*(1-p)

    genetic_algorithm = GeneticAlgorithm(C, p, q_1 if exact_n0 else None, q_2 if exact_n0 else None, degree, seed)
    genetic_algorithm.get_initial_guesses(algorithm_config.get_granularity(0), algorithm_config.get_population_size(0))
    genetic_algorithm.sort_population()

    for i in range(algorithm_config.get_num_iterations()):
        print(f"Starting generation {i} with best element. Gen_size: {len(genetic_algorithm.population)}, granularity:{algorithm_config.get_granularity(i)}:")
        genetic_algorithm.print_best()
        genetic_algorithm.get_new_population(algorithm_config.get_population_multiplier(i), algorithm_config.get_granularity(i))
        genetic_algorithm.sort_population()
        genetic_algorithm.shrink_population(algorithm_config.get_population_size(i))

    bound_quantiles, bound_vals, epsilon, d, sg_cutoff = genetic_algorithm.get_best_bound()
    validate_bound(bound_vals, bound_quantiles, epsilon, d, sg_cutoff, C, c_0, delta_1)

    return VarianceBoundWitness(genetic_algorithm.population[0].epsilon,
                                -1, -1, degree, None, genetic_algorithm.population[0].d, 
                                -genetic_algorithm.fitness(genetic_algorithm.population[0]),
                                genetic_algorithm.population[0].epsilon, -1)