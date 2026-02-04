
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
                           solver_name = "CBC",
                           csv_path = None,
                           num_runs = 1):

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

    result: Dict[Expr, List[ValueNode]] = {}
    for i in range(num_runs):
        print("="*10+f"RUN {i}"+"="*10)

        res = compute_bounds_saturation(random_vars,
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
                solver_name=solver_name,
                hash_salt=i)
        result = {key: result.get(key,[])+ ([res[key]] if key in res else []) for key in res.keys() | result.keys()}
        

    if csv_path:
        with open(csv_path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(("monomial", "", "bound"))
            for expr, bounds in sorted(result.items(), key=lambda x: str(x[0])):
                ubs = set.union(*({ub.value for ub in b.ubs} for b in bounds))
                lbs = set.union(*({lb.value for lb in b.lbs} for b in bounds))
                for ub in sorted(ubs, key=lambda x: str(x)):
                    writer.writerow((str(expr), "<=", str(ub)))
                for lb in sorted(lbs, key=lambda x: str(x)):
                    writer.writerow((str(expr), ">=", str(lb)))
