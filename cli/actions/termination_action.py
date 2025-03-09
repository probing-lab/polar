from argparse import Namespace

from inputparser.parser import parse_program
from program.condition.true_cond import TrueCond
from program.transformer import normalize_program
from termination.termination_analyzer import TerminationAnalyzer
from .action import Action


class TerminationAction(Action):

    def __init__(self, cli_args: Namespace, smt=False, amber=False, variance_based=False, exact=False):
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
            raise NotImplementedError("To analyze probabilistic programs use --termination_amber or for polynomial random walks --termination_variance")
        # remove the loop condition from the program to allow for normalization
        program.loop_guard = TrueCond()
        program = normalize_program(program)

        TerminationAnalyzer.analyze(program, guard, smt=self.smt, amber=self.amber, variance_based=self.variance_based, exact=self.exact)
