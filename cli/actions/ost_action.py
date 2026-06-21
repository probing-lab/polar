from argparse import Action, Namespace

from inputparser.parser import parse_program
from extension_ost.moment_bound_using_ost import moment_bound_using_ost
from program.condition.true_cond import TrueCond
from program.transformer import normalize_program


class OstAction(Action):

    def __init__(self, cli_args: Namespace):
        self.cli_args = cli_args

    def __call__(self, *args, **kwargs):
        benchmark = args[0]
        program = parse_program(benchmark)
        guard = program.loop_guard

        print("Benchmark: ", benchmark)
        for var, lb in self.cli_args.lb:
            print(f"{var} >= {lb}")
        for var, ub in self.cli_args.ub:
            print(f"{var} <= {ub}")
        print("Solver: ", self.cli_args.milp_solver)
        print("Moments finite: ", self.cli_args.stopping_time_finite_moments)
        print("csv location: ", self.cli_args.csv_location)
        
        moment_bound_using_ost(benchmark,
                               self.cli_args.lb,
                               self.cli_args.ub,
                               self.cli_args.stopping_time_finite_moments,
                               solver_name=self.cli_args.milp_solver,
                               csv_path=self.cli_args.csv_location,
                               iter_var=self.cli_args.iter_var)