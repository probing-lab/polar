from argparse import Namespace
from .action import Action
from copy import deepcopy
from inputparser import Parser
from recurrences import RecBuilder
from symengine.lib.symengine_wrapper import sympify
from simulation import Simulator
from plots import StatesPlot, RunsPlot
from cli.common import prepare_program, get_moment, parse_program


class PlotAction(Action):
    cli_args: Namespace

    def __init__(self, cli_args: Namespace):
        self.cli_args = cli_args

    def __call__(self, *args, **kwargs):
        benchmark = args[0]
        monom = sympify(self.cli_args.plot)
        first_moment = second_moment = None
        if self.cli_args.plot_expectation or self.cli_args.plot_std:
            program = parse_program(benchmark, self.cli_args.transform_categoricals)
            program = prepare_program(program, self.cli_args)
            rec_builder = RecBuilder(program)
            solvers = {}
            solver_args = deepcopy(self.cli_args)
            solver_args.numeric_roots = True
            solver_args.numeric_croots = True
            solver_args.numeric_eps = 0.0000001
            if self.cli_args.plot_std:
                second_moment, _ = get_moment(monom ** 2, solvers, rec_builder, solver_args, program)
            first_moment, _ = get_moment(monom, solvers, rec_builder, solver_args, program)

        program = Parser().parse_file(benchmark, self.cli_args.transform_categoricals)
        simulator = Simulator(self.cli_args.simulation_iter)
        result = simulator.simulate(program, [monom], self.cli_args.number_samples)
        if self.cli_args.states_plot:
            p = StatesPlot(result, monom, self.cli_args.anim_time, self.cli_args.max_y, first_moment, second_moment)
        else:
            p = RunsPlot(result, monom, self.cli_args.yscale, self.cli_args.anim_iter, self.cli_args.anim_runs,
                         self.cli_args.anim_time, first_moment,
                         second_moment)
        if self.cli_args.save:
            print("Rendering and saving plot")
            p.save("plot")
            print("Plot saved.")
        else:
            p.draw()
