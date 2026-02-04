
from sympy import Symbol, oo, sympify
from extension_ost.saturation.saturation_based_bound_computation import compute_bounds_saturation
from inputparser.parser import Parser
from moment_bound_using_ost import moment_bound_using_ost
from program.condition.true_cond import TrueCond
from program.transformer import normalize_program
from recurrences.rec_builder import RecBuilder

program = Parser().parse_file("documentation/loops_ost_extension/running_example.prob")

moment_bound_using_ost(
            "documentation/loops_ost_extension/running_example.prob",
            {Symbol("x", real=True):1,
                Symbol("y", real=True):1,
                Symbol("z", real=True):2,
                Symbol("k", real=True):1},
            [(Symbol("x0", is_finite=True, positive=True),sympify(0), oo), 
                (Symbol("y0", is_finite=True),sympify(0), oo),
                (Symbol("z0", is_finite=True),sympify(0), oo)],
            {Symbol("x", real=True): sympify(-1), Symbol("k", real=True):sympify(1)},
            {Symbol("x", real=True): sympify(0)},
            stopping_time_moment_finite=2,
            num_sparsest_solutions=20,
            keep_nonoptimal_martingales=False,
            solver_name="CLP",
            csv_path="fig_1_strong_assumptions_clp.csv")
