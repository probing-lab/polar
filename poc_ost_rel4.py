from functools import reduce
from typing import List, Tuple
from sympy import Expr, Symbol, oo, preorder_traversal, solve, sympify
from extension_ost.bound_computation import compute_bounds
from extension_ost.bound_store import BoundStore
from inputparser.parser import Parser
from program.condition.true_cond import TrueCond
from program.distribution.distribution import DistributionFunction
from program.transformer import normalize_program
from recurrences.rec_builder import RecBuilder
from termination.martingales.branches.branch_builder import BranchBuilder

program = Parser().parse_file("documentation/loops_ost_extension/related_work_4.prob")
lg = program.loop_guard

program.loop_guard = TrueCond()


# Construct normal form so that Polar can analyze it
normalized_program = normalize_program(program)
recurrence_builder = RecBuilder(normalized_program)



deterministic_vars = set()
random_vars = set()

for var in normalized_program.original_variables:
    if not normalized_program.is_iteration_dependent(var):
        continue
    if normalized_program.dependency_info[var].ancestors & set(normalized_program.dist_variables + normalized_program.finite_variables):
        random_vars.add(var)
    else:
        deterministic_vars.add(var)


compute_bounds(random_vars,
               deterministic_vars,
               2,
               recurrence_builder,
               [(Symbol("money0", real=True, finite=True, positive=True),sympify(10), oo)],
               {Symbol("money", real=True): sympify(0), Symbol("k", real=True):sympify(1)},
               {Symbol("money", real=True): sympify(10)})
