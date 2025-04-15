from argparse import Namespace

from inputparser.parser import parse_program
from program.condition.true_cond import TrueCond
from program.transformer import normalize_program
from termination.termination_analyzer import TerminationAnalyzer
from termination.variance_based.exponent_approximation.genetic_algorithm_config import (
    MinMaxGeneticAlgorithmConfig,
)
from .action import Action


class TerminationAction(Action):

    def __init__(
        self,
        cli_args: Namespace,
        smt=False,
        amber=False,
        variance_based=False,
        exact=False,
    ):
        self.cli_args = cli_args
        self.smt = smt
        self.amber = amber
        self.variance_based = variance_based
        self.exact = exact

    def __call__(self, *args, **kwargs):
        benchmark = args[0]
        program = parse_program(benchmark)
        guard = program.loop_guard
        if program.is_probabilistic and not (self.amber or self.variance_based):
            raise NotImplementedError(
                "To analyze probabilistic programs use --termination_amber or for polynomial random walks --termination_variance"
            )
        # remove the loop condition from the program to allow for normalization
        program.loop_guard = TrueCond()
        program = normalize_program(program)

        TerminationAnalyzer.analyze(
            program,
            guard,
            smt=self.smt,
            amber=self.amber,
            variance_based=self.variance_based,
            exact=self.exact,
            genetic_algorithm_config=MinMaxGeneticAlgorithmConfig(
                self.cli_args.num_generations,
                self.cli_args.min_gran,
                self.cli_args.max_gran,
                self.cli_args.min_pop,
                self.cli_args.max_pop,
                self.cli_args.mutation_rate,
                self.cli_args.crossover_rate,
                self.cli_args.lin_solver,
                self.cli_args.degree_population_shrink,
                self.cli_args.degree_granularity_growth,
            ),
            seed=self.cli_args.seed,
        )
