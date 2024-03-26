from argparse import ArgumentParser as ArgParser
import glob

import settings


def _set_settings(args):
    settings.transform_categoricals = args.transform_categoricals
    settings.cond2arithm = args.cond2arithm
    settings.disable_type_inference = args.disable_type_inference
    settings.type_fp_iterations = args.type_fp_iterations
    settings.numeric_roots = args.numeric_roots
    settings.numeric_croots = args.numeric_croots
    settings.trivial_guard = args.trivial_guard
    settings.exact_func_moments = args.exact_func_moments


class ArgumentParser:
    def __init__(self):
        self.argument_parser = ArgParser(
            description="Run Polar on probabilistic loops stored in files"
        )
        self.argument_parser.add_argument(
            "benchmarks",
            metavar="benchmarks",
            type=str,
            nargs="+",
            help="A list of benchmarks to run Polar on",
        )
        self.argument_parser.add_argument(
            "--at_n",
            dest="at_n",
            default=-1,
            type=int,
            help="Iteration number to evaluate the expressions at",
        )
        self.argument_parser.add_argument(
            "--simulate",
            action="store_true",
            default=False,
            help="If set Polar simulates the program",
        )
        self.argument_parser.add_argument(
            "--invariants",
            action="store_true",
            default=False,
            help="If set Polar computes all polynomial invariants among the goals.",
        )
        self.argument_parser.add_argument(
            "--simulation_iter",
            dest="simulation_iter",
            default=100,
            type=int,
            help="Number of iterations after which the simulation stops.",
        )
        self.argument_parser.add_argument(
            "--number_samples",
            dest="number_samples",
            default=100,
            type=int,
            help="The number of samples to simulate.",
        )
        self.argument_parser.add_argument(
            "--goals",
            dest="goals",
            type=str,
            default=[],
            nargs="+",
            help="A list of goals Polar should compute or simulate",
        )
        self.argument_parser.add_argument(
            "--gram_charlier",
            dest="gram_charlier",
            type=str,
            default="",
            help="A monomial to perform the gram-charlier expansion with",
        )
        self.argument_parser.add_argument(
            "--gram_charlier_order",
            dest="gram_charlier_order",
            default=4,
            type=int,
            help="The number of cumulants to compute for the expansion",
        )
        self.argument_parser.add_argument(
            "--cornish_fisher",
            dest="cornish_fisher",
            type=str,
            default="",
            help="A monomial to perform the cornish-fisher expansion with",
        )
        self.argument_parser.add_argument(
            "--cornish_fisher_order",
            dest="cornish_fisher_order",
            default=4,
            type=int,
            help="The number of cumulants to compute for the expansion.",
        )
        self.argument_parser.add_argument(
            "--plot", dest="plot", type=str, default="", help="A monomial to plot"
        )
        self.argument_parser.add_argument(
            "--states_plot",
            action="store_true",
            default=False,
            help="If true the states distribution gets plotted in an animated way",
        )
        self.argument_parser.add_argument(
            "--plot_expectation",
            action="store_true",
            default=False,
            help="If true the exact expectation gets included in the plot",
        )
        self.argument_parser.add_argument(
            "--plot_std",
            action="store_true",
            default=False,
            help="If true the exact standard deviation gets included in the plot",
        )
        self.argument_parser.add_argument(
            "--max_y",
            dest="max_y",
            type=int,
            help="The maximum value on the y axis of the states plot.",
        )
        self.argument_parser.add_argument(
            "--anim_iter",
            action="store_true",
            default=False,
            help="If true the iterations are animated in the runs plot.",
        )
        self.argument_parser.add_argument(
            "--anim_runs",
            action="store_true",
            default=False,
            help="If true the runs are animated in the runs plot.",
        )
        self.argument_parser.add_argument(
            "--anim_time",
            dest="anim_time",
            default=10.0,
            type=float,
            help="The duration of plot animations in seconds. (Only the saved plots adhere to this option)",
        )
        self.argument_parser.add_argument(
            "--anim_iterations",
            action="store_true",
            default=False,
            help="If true the iterations are animated in the runs plot",
        )
        self.argument_parser.add_argument(
            "--yscale",
            dest="yscale",
            type=str,
            default="linear",
            help="The y-scale for the plot",
        )
        self.argument_parser.add_argument(
            "--save",
            action="store_true",
            default=False,
            help="If true and in plotting mode the plot is saved to a file.",
        )
        self.argument_parser.add_argument(
            "--transform_categoricals",
            action="store_true",
            default=settings.transform_categoricals,
            help="If set transform categorical assignments into multiple individual assignments",
        )
        self.argument_parser.add_argument(
            "--cond2arithm",
            action="store_true",
            default=settings.cond2arithm,
            help="If set converts all conditions to arithmetic ahead of the main computation",
        )
        self.argument_parser.add_argument(
            "--disable_type_inference",
            action="store_true",
            default=settings.disable_type_inference,
            help="If set there won't be automatic type inference",
        )
        self.argument_parser.add_argument(
            "--type_fp_iterations",
            dest="type_fp_iterations",
            default=settings.type_fp_iterations,
            type=int,
            help="Number of iterations in the fixedpoint computation of the type inference",
        )
        self.argument_parser.add_argument(
            "--numeric_roots",
            action="store_true",
            default=settings.numeric_roots,
            help="If set the roots in the recurrence computation will be computed numerically",
        )
        self.argument_parser.add_argument(
            "--numeric_croots",
            action="store_true",
            default=settings.numeric_croots,
            help="If set the complex roots in the recurrence computation will be computed numerically",
        )
        self.argument_parser.add_argument(
            "--tail_bound_moments",
            dest="tail_bound_moments",
            default=2,
            type=int,
            help="The number of moments to consider when computing Markov's inequality",
        )
        self.argument_parser.add_argument(
            "--trivial_guard",
            action="store_true",
            default=settings.trivial_guard,
            help="If set any loop guard will be overridden with 'true'",
        )
        self.argument_parser.add_argument(
            "--after_loop",
            action="store_true",
            default=False,
            help="If set fixedpoints/limits are used to compute the moments after the loop",
        )
        self.argument_parser.add_argument(
            "--exact_func_moments",
            action="store_true",
            default=settings.exact_func_moments,
            help="If set, moments of functions of distributions which would be transcendental won't be approximated by rationals",
        )
        self.argument_parser.add_argument(
            "--solvability_check",
            action="store_true",
            default=False,
            help="If set Polar checks if the goal is effective/solvable and throws and error if not",
        )
        self.argument_parser.add_argument(
            "--synth_unsolv_inv",
            dest="synth_unsolv_inv",
            type=str,
            nargs="*",
            help="The variables to include in the candidate for synthesizing an invariant for an unsolvable loop",
        )
        self.argument_parser.add_argument(
            "--inv_deg",
            dest="inv_deg",
            default=2,
            type=int,
            help="The maximum degree of the invariant to synthesize given an unsolvable loop",
        )
        self.argument_parser.add_argument(
            "--bif_to_prob",
            dest="bif_to_prob",
            type=str,
            help="Transform BIF-file to PROB-file and store in file named as argument",
        )
        self.argument_parser.add_argument(
            "--sample_time_until",
            dest="sample_time_until",
            type=str,
            help="""Mean number of samples necessary to see the given (conjunctive) conditions in a
            Baysian Network (given as BIF) (format: VAR = VALUE, VAR = VALUE, ..)""",
        )
        self.argument_parser.add_argument(
            "--exact_inference",
            dest="exact_inference",
            type=str,
            help="""Raw Moment of variable given some other variables in a Baysian Network (given as BIF)
            (format VAR**k | VAR = VAL, VAR = VAL, ..)""",
        )
        self.argument_parser.add_argument(
            "-sens",
            "--sensitivity_analysis",
            dest="sensitivity_analysis",
            type=str,
            help="Get sensitivity of goal with respect to the symbolic constants",
        )
        self.argument_parser.add_argument(
            "-sens_diff",
            "--sensitivity_analysis_diff",
            dest="sensitivity_analysis_diff",
            type=str,
            help="""Get sensitivity of goal with respect to the
            symbolic constants by differentiating the closed form solution""",
        )
        self.argument_parser.add_argument(
            "--synth_solv_loop",
            dest="synth_solv_loop",
            type=str,
            nargs="*",
            help="Synthesize a solvable loop from an unsolvable loop",
        )

    def parse_args(self):
        args = self.argument_parser.parse_args()
        args.benchmarks = [b for bs in map(glob.glob, args.benchmarks) for b in bs]

        if len(args.benchmarks) == 0:
            raise Exception(
                "No benchmark given. Run with '--help' for more information."
            )

        _set_settings(args)
        return args

    def get_defaults(self):
        return self.argument_parser.parse_args({"benchmarks": []})
