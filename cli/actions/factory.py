from argparse import Namespace

from cli.actions.bayesian_network_action import BayesNetworkAction
from .simulation_action import Action, SimulationAction
from .plot_action import PlotAction
from .gram_charlier_action import GramCharlierAction
from .cornish_fisher_action import CornishFisherAction
from .mc_combination_action import MCCombinationAction
from .print_benchmark_action import PrintBenchmarkAction
from .goals_action import GoalsAction

class ActionFactory:

    @classmethod
    def create_action(cls, cli_args: Namespace) -> Action:
        if cli_args.sample_time_until:
            return BayesNetworkAction(cli_args)
        if cli_args.simulate:
            return SimulationAction(cli_args)
        if cli_args.goals or cli_args.invariants:
            return GoalsAction(cli_args)
        if cli_args.plot:
            return PlotAction(cli_args)
        if cli_args.gram_charlier:
            return GramCharlierAction(cli_args)
        if cli_args.cornish_fisher:
            return CornishFisherAction(cli_args)
        if cli_args.mc_comb is not None:
            return MCCombinationAction(cli_args)

        return PrintBenchmarkAction(cli_args)
