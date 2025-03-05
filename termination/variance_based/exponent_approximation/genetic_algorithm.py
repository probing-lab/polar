from dataclasses import dataclass
from functools import cache
from math import exp, log
from typing import List

import numpy as np
from termination.polynomial.termination_witness import TerminationWitness
from termination.variance_based.exponent_approximation.closed_form_bound import get_closed_form_bound_asymptotic
from termination.variance_based.exponent_approximation.inductive_bound import PrecisionException, _check_model, _compute_b
from termination.variance_based.variance_bound_witness import VarianceBoundWitness

@dataclass
class InductiveBoundSpecification:
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
    def __init__(self, C:float, delta_1: float, delta_2:float, c_0:float, degree:float, seed=None):
        self.C = C
        self.delta_1 = delta_1
        self.delta_2 = delta_2
        self.c_0 = c_0
        self. degree = degree
        self.rand_gen = np.random.default_rng(seed)

        self.population: List[InductiveBoundSpecification] = None

    @cache
    def fitness(self, spec: InductiveBoundSpecification):
        try:
            if _check_model(spec.d, spec.epsilon, self.C, self.delta_2, self.c_0, 
                            spec.granularity, spec.specification_end, spec.sg_cutoff, 
                            _compute_b(spec.epsilon, spec.d, self.C)) is not None:
                fitness = -log(1-spec.epsilon)/log((spec.d+1)**(1/self.degree) + self.delta_1) # compute the exponent. times (-1) to have positive fitness
                return fitness
            else:
                return 0
        except PrecisionException as ex:
            return 0
        
    def mutate(self, spec: InductiveBoundSpecification, new_granularity):
        d = spec.d
        epsilon = spec.epsilon
        granularity = new_granularity
        specification_end = spec.specification_end
        sg_cutoff = spec.sg_cutoff

        if self.rand_gen.random() < 0.3:
            d *=(self.rand_gen.random()*0.35+0.7)
        if self.rand_gen.random() < 0.3:
            epsilon *= (self.rand_gen.random()*0.1+0.95)
        if self.rand_gen.random() < 0.3:
            specification_end *= (self.rand_gen.random()*0.4 + 0.8)
        if self.rand_gen.random() < 0.3:
            sg_cutoff *= (self.rand_gen.random()*0.4 + 0.8)

        return InductiveBoundSpecification(d, epsilon, granularity, specification_end, sg_cutoff)

    def get_initial_guesses(self, granularity, size):
        exp_asym_bound = get_closed_form_bound_asymptotic(self.degree, self.C)/1.8
        self.population=[]
        for _ in range(size):
            epsilon = self.rand_gen.random()*0.3+0.1
            k =  exp((log(1-epsilon)/exp_asym_bound)) - self.delta_1
            d = k**self.degree - 1
            specification_end = self.rand_gen.random()*6+3
            sg_cutoff = self.rand_gen.random()*3.5+1.5
            self.population.append(InductiveBoundSpecification(
                d, epsilon, granularity, specification_end, sg_cutoff
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


def estimate_bound_exponent_inductive_bound_genetic(degree: float, C: float, delta_1: float, delta_2: float, c_0: float, n_0, granularity: int = 20, pop_size: int=30, pop_multiplier: int=5, num_generations=50, seed=0):
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

    genetic_algorithm = GeneticAlgorithm(C, delta_1, delta_2, c_0, degree, seed)
    new_granularity = granularity
    genetic_algorithm.get_initial_guesses(granularity, pop_size*5)
    genetic_algorithm.sort_population()

    for i in range(num_generations):
        print(f"Starting generation {i} with best element. Gen_size: {len(genetic_algorithm.population)}, granularity:{new_granularity}:")
        genetic_algorithm.print_best()
        new_granularity =  granularity+int(granularity*(i+1)**2/100)
        genetic_algorithm.get_new_population(pop_multiplier,new_granularity)
        genetic_algorithm.sort_population()
        genetic_algorithm.shrink_population(pop_size+int(pop_size*4/(i/2+1)))

    return VarianceBoundWitness(genetic_algorithm.population[0].epsilon,
                                delta_1, delta_2, degree, None, genetic_algorithm.population[0].d, 
                                -genetic_algorithm.fitness(genetic_algorithm.population[0]),
                                genetic_algorithm.population[0].epsilon, n_0)