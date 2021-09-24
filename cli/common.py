from inputparser import Parser
from program.transformer import *
from recurrences import RecBuilder
from recurrences.solver import RecurrenceSolver
from symengine.lib.symengine_wrapper import sympify
from sympy import limit, Symbol, oo
from utils import raw_moments_to_cumulants, is_moment_computable, eval_re
from termcolor import colored


def get_moment(monom, solvers, rec_builder, cli_args, program):
    if not is_moment_computable(monom, program):
        raise Exception(f"{monom} is not moment computable.")

    if monom not in solvers:
        recurrences = rec_builder.get_recurrences(monom)
        s = RecurrenceSolver(recurrences, cli_args.numeric_roots, cli_args.numeric_croots, cli_args.numeric_eps)
        solvers.update({sympify(m): s for m in recurrences.monomials})
    solver = solvers[monom]
    moment = solver.get(monom)

    if cli_args.after_loop:
        moment = limit(moment, Symbol("n", integer=True), oo)

    return moment, solver.is_exact


def get_all_cumulants(program, monom, max_cumulant, cli_args):
    rec_builder = RecBuilder(program)
    solvers = {}
    moments, is_exact = get_all_moments(monom, max_cumulant, solvers, rec_builder, cli_args, program)
    cumulants = raw_moments_to_cumulants(moments)
    if cli_args.at_n >= 0:
        cumulants = {i: eval_re(cli_args.at_n, c) for i, c in cumulants.items()}
    return cumulants


def get_all_moments(monom, max_moment, solvers, rec_builder, cli_args, program):
    moments = {}
    all_exact = True
    for i in reversed(range(1, max_moment + 1)):
        moment, is_exact = get_moment(monom ** i, solvers, rec_builder, cli_args, program)
        all_exact = all_exact and is_exact
        moments[i] = moment
    return moments, all_exact


def prepare_program(benchmark, cli_args):
    parser = Parser()
    program = parser.parse_file(benchmark, cli_args.transform_categoricals)

    print(colored("------------------", "magenta"))
    print(colored("- Parsed program -", "magenta"))
    print(colored("------------------", "magenta"))
    print(program)
    print()

    # Transform the loop-guard into an if-statement
    program = LoopGuardTransformer(cli_args.trivial_guard).execute(program)
    # Transform non-constant distributions parameters
    program = DistTransformer().execute(program)
    # Flatten if-statements
    program = IfTransformer().execute(program)
    # Make sure every variable has only 1 assignment
    program = MultiAssignTransformer().execute(program)
    # Create aliases for expressions in conditions.
    program = ConditionsReducer().execute(program)
    # Replace/Add constants in loop body
    program = ConstantsTransformer().execute(program)
    # Update program info like variables and symbols
    program = UpdateInfoTransformer(ignore_mc_variables=True).execute(program)
    # Infer types for variables
    if not cli_args.disable_type_inference:
        program = TypeInferer(cli_args.type_fp_iterations).execute(program)
    # Update dependency graph (because finite variables are now detected)
    program = UpdateInfoTransformer().execute(program)
    # Turn all conditions into normalized form
    program = ConditionsNormalizer().execute(program)
    # Convert all conditions to arithmetic
    if cli_args.cond2arithm:
        program = ConditionsToArithm().execute(program)

    print(colored("-----------------------", "magenta"))
    print(colored("- Transformed program -", "magenta"))
    print(colored("-----------------------", "magenta"))
    print(program)
    print()
    return program
