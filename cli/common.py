from inputparser import Parser
from program.transformer import LoopGuardTransformer, DistTransformer, IfTransformer, MultiAssignTransformer, \
    ConditionsReducer, ConstantsTransformer, UpdateInfoTransformer, TypeInferer, ConditionsNormalizer, \
    ConditionsToArithm
from recurrences import RecBuilder
from recurrences.solver import RecurrenceSolver
from symengine.lib.symengine_wrapper import sympify
from sympy import limit_seq, Symbol
from sympy import sympify as sympy_sympify
from utils import raw_moments_to_cumulants, is_moment_computable, eval_re, unpack_piecewise, get_max_case_in_piecewise
from termcolor import colored
from program.condition.not_cond import Not
from utils.expressions import get_monoms


def get_moment(monom, solvers, rec_builder, cli_args, program):
    if not is_moment_computable(monom, program):
        raise Exception(f"{monom} is not moment computable.")

    if monom not in solvers:
        recurrences = rec_builder.get_recurrences(monom)
        s = RecurrenceSolver(recurrences, cli_args.numeric_roots, cli_args.numeric_croots, cli_args.numeric_eps)
        solvers.update({sympify(m): s for m in recurrences.monomials})
    solver = solvers[monom]
    moment = solver.get(monom)

    return moment, solver.is_exact


def get_moment_poly(poly, solvers, rec_builder, cli_args, program):
    expanded_poly = poly.expand()
    monoms = get_monoms(expanded_poly)
    is_exact_acc = True
    moments = {}
    for _, monom in monoms:
        moment, is_exact = get_moment(monom, solvers, rec_builder, cli_args, program)
        moments[monom] = moment
        is_exact_acc = is_exact_acc and is_exact
    return expanded_poly.subs_dict(moments), is_exact_acc


def get_all_cumulants(program, monom, max_cumulant, cli_args):
    rec_builder = RecBuilder(program)
    solvers = {}
    moments, is_exact = get_all_moments(monom, max_cumulant, solvers, rec_builder, cli_args, program)
    cumulants = raw_moments_to_cumulants(moments)
    if cli_args.at_n >= 0:
        cumulants = {i: eval_re(cli_args.at_n, c) for i, c in cumulants.items()}
    return cumulants


def get_all_cumulants_after_loop(program, monom, max_cumulant, cli_args):
    rec_builder = RecBuilder(program)
    solvers = {}
    moments, is_exact = get_all_moments_after_loop(monom, max_cumulant, solvers, rec_builder, cli_args, program)
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


def get_all_moments_after_loop(monom, max_moment, solvers, rec_builder, cli_args, program):
    moments_after_loop = {}
    all_exact = True
    for i in reversed(range(1, max_moment + 1)):
        moment_after_loop, is_exact = get_moment_after_loop(monom ** i, solvers, rec_builder, cli_args, program)
        all_exact = all_exact and is_exact
        moments_after_loop[i] = moment_after_loop
    return moments_after_loop, all_exact


def get_moment_after_loop(monom, solvers, rec_builder, cli_args, program):
    """
    Calculates the moment of a monomial after loop termination.
    """
    negated_loop_guard = Not(program.original_loop_guard).to_arithm(program)
    moment_guard, is_exact_guard = get_moment_poly(
        negated_loop_guard, solvers, rec_builder, cli_args, program)
    moment_monom_guard, is_exact_monom_guard = get_moment_poly(
        monom*negated_loop_guard, solvers, rec_builder, cli_args, program)

    conditional_expected_value = sympy_sympify(moment_monom_guard/moment_guard)
    moment_after_loop = transform_to_after_loop(conditional_expected_value)
    return moment_after_loop, (is_exact_guard and is_exact_monom_guard)


def transform_to_after_loop(element):
    def trans_single(e):
        return limit_seq(unpack_piecewise(e), Symbol("n", integer=True))

    if isinstance(element, dict):
        return {k: trans_single(v) for k, v in element.items()}
    else:
        return trans_single(element)


def print_is_exact(is_exact):
    if is_exact:
        print(colored("Solution is exact", "green"))
    else:
        print(colored("Solution is rounded", "yellow"))


def prettify_piecewise(expression):
    max_case = get_max_case_in_piecewise(expression)
    if max_case < 0:
        return str(expression)
    special_cases = []
    for n in range(max_case + 1):
        special_cases.append(str(expression.subs({Symbol("n", integer=True): n})))
    return "; ".join(special_cases) + "; " + str(unpack_piecewise(expression))


def prepare_program(benchmark, cli_args):
    parser = Parser()
    program = parser.parse_file(benchmark, cli_args.transform_categoricals)

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

    return program
