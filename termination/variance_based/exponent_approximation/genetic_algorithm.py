from dataclasses import dataclass
from functools import cache
from math import exp, log
from typing import List
from sympy import Expr, Symbol, sympify, degree
from scipy.special import zeta

import numpy as np
from termination.polynomial.termination_witness import TerminationWitness
from termination.variance_based.exponent_approximation.bound_validation import validate_bound
from termination.variance_based.exponent_approximation.closed_form_bound import _get_c_d_prime, get_closed_form_bound_asymptotic
from termination.variance_based.exponent_approximation.converging_constants import compute_c_0, compute_delta_cb, compute_delta_prime, get_k_delta, get_n0_from_c0
from termination.variance_based.exponent_approximation.genetic_algorithm_config import GeneticAlgorithmConfig
from termination.variance_based.exponent_approximation.inductive_bound import PrecisionException, _check_model, _compute_b
from termination.variance_based.variance_bound_witness import VarianceBoundWitness

N = Symbol("n", integer=True)

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
    def __init__(self, C:float, p: float, q1: Expr, q2: Expr, initial_value:float|Expr, degree:float, seed=None):
        self.C = C
        self.p = p
        self.q1 = q1
        self.q2 = q2
        self.initial_value = initial_value
        self.degree = degree
        self.rand_gen = np.random.default_rng(seed)

        self.population: List[InductiveBoundSpecification] = None

    def _get_delta_1(self, n0):
        if self.q1 is None or self.q2 is None:
            return 1e-8
        return compute_delta_cb(n0, self.p, self.q1.as_expr(), self.q2.as_expr(), self.initial_value)

    def _get_delta_prime(self, n0):
        if self.q1 is None or self.q2 is None:
            return 1+1e-8
        return compute_delta_prime(n0, self.p, self.q1, self.q2)
        
    def _get_c_0(self, n0, k):
        if self.q1 is None or self.q2 is None:
            return 1e-8
        return compute_c_0(n0, self.p, self.q1.as_expr(), self.q2.as_expr(), k,  self.initial_value)

    def _get_n0_from_c0(self, c0):
        if self.q1 is None or self.q2 is None:
            return 0
        return get_n0_from_c0(self.p, self.q1.as_expr(), self.q2.as_expr(), c0, self.initial_value)
    
    def _get_k_delta(self, n0, k):
        if self.q1 is None or self.q2 is None:
            return 1e-8
        return get_k_delta(n0, k)

    @cache
    def fitness(self, spec: InductiveBoundSpecification):
        try:
            delta_1 = self._get_delta_1(spec.n0)
            delta_prime = self._get_delta_prime(spec.n0)

            k = ((spec.d+1)*delta_prime)**(1/self.degree)
            k_delta = self._get_k_delta(spec.n0, k)
            c_0 = self._get_c_0(spec.n0, k)

            if _check_model(spec.d, spec.epsilon, self.C, delta_1, c_0, 
                            spec.granularity, spec.specification_end, spec.sg_cutoff, 
                            _compute_b(spec.epsilon, spec.d, self.C)) is not None:
                
                exponent_fitness = log(1-spec.epsilon)/log(k+k_delta) # compute the exponent.
                abs_bound = np.infty
                coeff = np.infty
                try:
                    if exponent_fitness < -1 and self.q1 is not None and self.q2 is not None:
                        # compute actual bound
                        coeff = (1/(1-spec.epsilon))**((log(spec.n0, k))+2)
                        
                        series_sum = zeta(-exponent_fitness, spec.n0+1)*coeff + spec.n0 # TODO: The zeta function is an over-approximation, because actually the elements are bounded by 1 from above (would need the partial sum from n_0).
                        abs_bound = series_sum
                    return (abs_bound, exponent_fitness, coeff) # fitness has two dimensions: the first is the actual bound (absolute value), the second is the exponent
                except Exception as ex:
                    print(f"Warning: encountered exception: {ex}")
                    return (np.infty, 0, np.infty)
            else:
                return (np.infty, 0, np.infty)
        except PrecisionException as ex:
            return (np.infty, 0, np.infty)
        
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
        return res, res_vals, spec.epsilon, spec.d, spec.specification_end+spec.sg_cutoff, c_0, delta_1
        
    def mutate(self, spec: InductiveBoundSpecification, new_granularity):
        d = spec.d
        epsilon = spec.epsilon
        granularity = new_granularity
        specification_end = spec.specification_end
        sg_cutoff = spec.sg_cutoff
        n0 = spec.n0

        if self.rand_gen.random() < 0.4: # small step
            d *=(self.rand_gen.random()*0.1+0.92)
        elif self.rand_gen.random() < 0.3:
            d *=(self.rand_gen.random()*0.5+0.55)
        if self.rand_gen.random() < 0.4: # small step
            epsilon *= (self.rand_gen.random()*0.08+0.96)
        if self.rand_gen.random() < 0.3:
            specification_end *= (self.rand_gen.random()*0.4 + 0.8)
        if self.rand_gen.random() < 0.3:
            sg_cutoff *= (self.rand_gen.random()*0.4 + 0.8)
        if self.rand_gen.random() < 0.6:
            n0 *= (self.rand_gen.random()+0.1 + (0.5 if self.fitness(spec)[0]==np.infty else 0))

        return InductiveBoundSpecification(n0, d, epsilon, granularity, specification_end, sg_cutoff)
    
    def crossover(self, spec1: InductiveBoundSpecification, spec2: InductiveBoundSpecification, new_granularity):
        # every gene is randomly selected from one parent
        n0 = spec1.n0 if self.rand_gen.random() < 0.5 else spec2.n0
        d = spec1.d if self.rand_gen.random() < 0.5 else spec2.d
        epsilon = spec1.epsilon if self.rand_gen.random() < 0.5 else spec2.epsilon
        specification_end = spec1.specification_end if self.rand_gen.random() < 0.5 else spec2.specification_end
        sg_cutoff = spec1.sg_cutoff if self.rand_gen.random() < 0.5 else spec2.sg_cutoff

        return InductiveBoundSpecification(n0, d, epsilon, new_granularity, specification_end, sg_cutoff)

    def get_initial_guesses(self, granularity, size, adapt_d=True):
        exp_asym_bound = get_closed_form_bound_asymptotic(self.degree, self.C)/1.8
        n0 = self._get_n0_from_c0(0.001)
        
        self.population=[]
        c_prime, d_prime = _get_c_d_prime(self.C) # this serves just as a heuristic, to always guess in the somewhat right area
        for _ in range(size):
            epsilon = self.rand_gen.random()*0.3+0.1
            delta_prime = self._get_delta_prime(n0)
            k =  exp((log(1-epsilon)/exp_asym_bound))
            d = k**self.degree*delta_prime - 1
            sg_cutoff_total = self.rand_gen.random()*c_prime+5.5
            specification_end = sg_cutoff_total - (self.rand_gen.random()*4.5+1)
            sg_cutoff = sg_cutoff_total-specification_end
            spec = InductiveBoundSpecification(
                n0, d, epsilon, granularity, specification_end, sg_cutoff
            )
            if adapt_d:
                while self.fitness(spec)[1]!=0:
                    spec.d /= 2
                spec.d *= 2
            self.population.append(spec)


    def get_new_population(self, mutation_multipier, crossover_multiplier, new_granularity):
        elems = self.rand_gen.choice(self.population, mutation_multipier*len(self.population), replace=True)
        mutations = [self.mutate(spec, new_granularity) for spec in elems]
        
        crossover_parents = [tuple(self.rand_gen.choice(self.population, size=2, replace=False)) for _ in range(int(crossover_multiplier*len(self.population)))]
        children = [self.crossover(p1,p2,new_granularity) for p1,p2 in crossover_parents]
        self.population = self.population+mutations+children

    def sort_population(self):
        self.population = sorted(self.population, key=lambda spec: self.fitness(spec), reverse=False)
        
    def shrink_population(self, size):
        self.population = self.population[:size]

    def print_best(self):
        print(f"exponent: {self.fitness(self.population[0])},epsilon: {self.population[0].epsilon}, d: {self.population[0].d}, spec_end: {self.population[0].specification_end}, sg_cutoff: {self.population[0].sg_cutoff}, n0: {self.population[0].n0}")


def estimate_bound_exponent_inductive_bound_genetic(p:float, algorithm_config: GeneticAlgorithmConfig, q_1: Expr, q_2: Expr, initial_expr=None, exact_n0=False, seed=None):
    """Create an upper bound for the exponent m of the bound $P(T\\geq t) \\leq Bn^{m}$. This method leverages a linear solver to do so.
    """
    assert 0 < p and p<1, "p must be a valid percentage between ]0;1["
    if (initial_expr is None or not sympify(initial_expr).is_number) and exact_n0:
        raise Exception("Can not compute exact bound for stopping time, when initial value of loop guard is unknown")
    C = 4*p*(1-p)
    var_degree = max(degree(q_1, N), degree(q_2, N)) *2+1
    genetic_algorithm = GeneticAlgorithm(C, p, q_1 if exact_n0 else None, q_2 if exact_n0 else None, initial_expr, var_degree, seed)
    genetic_algorithm.get_initial_guesses(algorithm_config.get_granularity(0), algorithm_config.get_population_size(0))
    genetic_algorithm.sort_population()

    for i in range(algorithm_config.get_num_iterations()):
        print(f"Starting generation {i} with best element. Gen_size: {len(genetic_algorithm.population)}, granularity:{algorithm_config.get_granularity(i)}:")
        genetic_algorithm.print_best()
        genetic_algorithm.get_new_population(algorithm_config.get_population_mutation_multiplier(i), 
                                             algorithm_config.get_population_crossover_multiplier(i), 
                                             algorithm_config.get_granularity(i))
        genetic_algorithm.sort_population()
        genetic_algorithm.shrink_population(algorithm_config.get_population_size(i))

    bound_quantiles, bound_vals, epsilon, d, sg_cutoff, c_0_res, delta_1_res = genetic_algorithm.get_best_bound()
    validate_bound(bound_vals, bound_quantiles, epsilon, d, sg_cutoff, C, c_0_res, delta_1_res)

    return VarianceBoundWitness(genetic_algorithm.fitness(genetic_algorithm.population[0])[1],
                                Symbol("B") if not exact_n0 else genetic_algorithm.fitness(genetic_algorithm.population[0])[2],
                                genetic_algorithm.population[0].n0 if exact_n0 else None)
