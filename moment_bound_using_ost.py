
import csv
from typing import Dict, List, Tuple
from sympy import Expr, Symbol, oo, sympify
from extension_ost.saturation.saturation_based_bound_computation import compute_bounds_saturation
from extension_ost.saturation.saturation_rules.value_node import ValueNode
from inputparser.parser import Parser
from program.condition.true_cond import TrueCond
from program.transformer import normalize_program
from recurrences.rec_builder import RecBuilder

def moment_bound_using_ost(file_path: str,
                           program_vars: Dict[Symbol, int],
                           initial_values: Tuple[Symbol, Expr, Expr],
                           lower_bounds_after_termination: Dict[Symbol, int],
                           upper_bounds_after_termination: Dict[Symbol, int],
                           stopping_time_moment_finite: int,
                           use_minkovski = False,
                           num_sparsest_solutions = 20,
                           keep_nonoptimal_martingales = False,
                           solver_name = "CLP",
                           csv_path = None):

    program = Parser().parse_file(file_path)
    lg = program.loop_guard
    print(f"Loop guard: {lg}")

    program.loop_guard = TrueCond()

    # Construct normal form so that Polar can analyze it
    normalized_program = normalize_program(program)
    recurrence_builder = RecBuilder(normalized_program)

    deterministic_vars = set()
    random_vars = set()

    for var in normalized_program.original_variables:
        if not normalized_program.is_iteration_dependent(var):
            continue
        if normalized_program.is_dependent_vars({var}, normalized_program.dist_variables):
            random_vars.add(Symbol(str(var), real=True))
        else:
            deterministic_vars.add(Symbol(str(var), real=True))


    result: List[ValueNode] = compute_bounds_saturation(random_vars,
                deterministic_vars,
                stopping_time_moment_finite,
                program_vars,
                recurrence_builder,
                initial_values,
                lower_bounds_after_termination,
                upper_bounds_after_termination,
                num_sparsest_solutions=num_sparsest_solutions,
                use_minkowski=use_minkovski,
                keep_non_optimal_martingales=keep_nonoptimal_martingales,
                solver_name=solver_name)

    if csv_path:
        with open(csv_path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(("monomial", "", "bound"))
            for node in sorted(result.values(), key=lambda x: str(x.name)):
                for ub in sorted(node.ubs, key=lambda x: str(x)):
                    writer.writerow((str(node.name), "<=", str(ub)))
                for lb in sorted(node.lbs, key=lambda x: str(x)):
                    writer.writerow((str(node.name), ">=", str(lb)))
