from argparse import Namespace

from cli.actions.bayesian_network_action import BayesNetworkAction
from cli.actions.sensitivity_action import SensitivityAction
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
        if cli_args.sample_time_until or cli_args.exact_inference or cli_args.bif_to_prob:
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
        if cli_args.sensitivity_analysis or cli_args.sensitivity_analysis_diff:
            return SensitivityAction(cli_args)

        return PrintBenchmarkAction(cli_args)
