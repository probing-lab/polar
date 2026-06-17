from functools import reduce
from typing import List, Tuple
from sympy import Expr, Rational, Symbol, oo, preorder_traversal, solve, sympify
from extension_ost.bound_computation import compute_bounds
from extension_ost.bound_store import BoundStore
from extension_ost.helpers import Expexted
from extension_ost.saturation.saturation_based_bound_computation import compute_bounds_saturation
from inputparser.parser import Parser
from moment_bound_using_ost import moment_bound_using_ost
from program.condition.true_cond import TrueCond
from program.distribution.distribution import DistributionFunction
from program.transformer import normalize_program
from recurrences.rec_builder import RecBuilder
from termination.martingales.branches.branch_builder import BranchBuilder
import argparse

parser = argparse.ArgumentParser(description="Reproduce Figure 2 (bottom part of table)")

parser.add_argument("-c", "--count", type=int, default=3, help="The number of times to invoke the saturation algorithm")
parser.add_argument("-o", "--output", type=str, default=None, help="The (csv) output file location")
parser.add_argument("-s", "--solver", type=str, default="CBC", help="The linear solver to use (CBC/GUROBI/...)")

args = parser.parse_args()

moment_bound_using_ost(
    "documentation/loops_ost_extension/running_example_unbounded.prob",
    {Symbol("x", real=True): 1,
     Symbol("z", real=True): 1,
     Symbol("k", real=True): 1},
    [(Symbol("x0", is_finite=True, positive=True), sympify(0), oo)],
    {Symbol("k", real=True): sympify(1),
     Expexted(Symbol("x", real=True)): -sympify(Rational(13, 10))},
    {Symbol("x", real=True): sympify(0),
     Expexted(Symbol("x", real=True)**2): sympify(Rational(23, 10))},
    stopping_time_moment_finite=2,
    num_sparsest_solutions=20,
    keep_nonoptimal_martingales=False,
    use_minkovski=False,
    solver_name=args.solver,
    csv_path=args.output,
    num_runs=args.count)
