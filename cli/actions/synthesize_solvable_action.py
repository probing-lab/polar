from argparse import Namespace
from .action import Action
from cli.common import prepare_program, parse_program
from termcolor import colored
from program.solvable_synthesizer import SolvableSynthesizer
from recurrences import RecBuilder
from program import Program
from program.assignment import PolyAssignment

class SynthSolvAction(Action):
    cli_args: Namespace

    def __init__(self, cli_args: Namespace):
        self.cli_args = cli_args

    def __call__(self, *args, **kwargs):
        benchmark = args[0]
        combination_deg = self.cli_args.synth_solv

        program = parse_program(benchmark, self.cli_args.transform_categoricals)
        program = prepare_program(program, self.cli_args)

        if len(program.non_mc_variables) == 0:
            print(f"Loop in {benchmark} is already solvable.")
            return

        combination_vars = []
        for var in program.non_mc_variables:
            if var in program.original_variables:
                combination_vars.append(var)

        print(colored("-------------------", "cyan"))
        print(colored("- Analysis Result -", "cyan"))
        print(colored("-------------------", "cyan"))
        print()

        combinations = SolvableSynthesizer.synthesize(
            combination_vars, combination_deg, program, self.cli_args.numeric_roots, self.cli_args.numeric_croots,
            self.cli_args.numeric_eps
        )

        solvable_loop_body = []
        solvable_loop_variables = []

        if combinations is None:
            print(f"No combination found with degree {combination_deg}. Try using higher degrees.")
            return program
        else:
            for combination in combinations:
                for poly_assign in program.loop_body:
                    var = poly_assign.variable
                    if var in program.mc_variables:
                        solvable_loop_body.append(poly_assign)
                        solvable_loop_variables.append(var)

                comb_var, comb_var_assign = combination[0], combination[1]
                solvable_loop_body.append(PolyAssignment(comb_var, [comb_var_assign], [1]))
                solvable_loop_variables.append(comb_var)

        solvable_program = Program([], solvable_loop_variables, solvable_loop_variables, program.initial,
                                   program.loop_guard, solvable_loop_body, program.is_probabilistic)
        solvable_program.typedefs = program.typedefs

        print("Synthesized solvable loop: ")
        print(solvable_program)
        return solvable_program