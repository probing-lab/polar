from abc import ABC, abstractmethod


class GeneticAlgorithmConfig(ABC):
    @abstractmethod
    def get_granularity(self, iteration):
        pass

    @abstractmethod
    def get_population_size(self, iteration):
        pass

    @abstractmethod
    def get_population_mutation_multiplier(self, iteration):
        pass

    @abstractmethod
    def get_population_crossover_multiplier(self, iteration):
        pass

    @abstractmethod
    def get_num_iterations(self):
        pass

class MinMaxQuadraticAlgorithmConfig(GeneticAlgorithmConfig):
    def __init__(self, num_iterations, min_granularity, max_granularity, min_population, max_population, mutation_multiplier, crossover_multiplier, degree_pop=1):
        self.granularity_offset = min_granularity
        self.granularity_coeff = (max_granularity-min_granularity)/num_iterations**2

        self.max_population = max_population
        self.population_coeff = (min_population-max_population)/num_iterations**degree_pop
        self.degree_pop = degree_pop

        self.mutation_multiplier = mutation_multiplier
        self.crossover_multiplier = crossover_multiplier
        self.num_iterations = num_iterations

    def get_granularity(self, iteration):
        gr = int(self.granularity_offset+(iteration+1)**2*self.granularity_coeff)
        return gr
    
    def get_population_mutation_multiplier(self, iteration):
        return self.mutation_multiplier

    def get_population_crossover_multiplier(self, iteration):
        return self.crossover_multiplier
    
    def get_num_iterations(self):
        return self.num_iterations
    
    def get_population_size(self, iteration):
        return int(self.max_population+ self.population_coeff*(iteration+1)**self.degree_pop)