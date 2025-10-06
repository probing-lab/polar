from functools import reduce
from typing import List, Tuple
from sympy import Expr, Symbol, oo, preorder_traversal, solve, sympify
from extension_ost.bound_computation import compute_bounds
from extension_ost.bound_store import BoundStore
from extension_ost.expectation_map import get_expectation_maps
from inputparser.parser import Parser
from program.condition.true_cond import TrueCond
from program.distribution.distribution import DistributionFunction
from program.transformer import normalize_program
from recurrences.rec_builder import RecBuilder
from termination.martingales.branches.branch_builder import BranchBuilder

program = Parser().parse_file("documentation/loops_ost_extension/nested_loops/loop1/inner.prob")
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
        random_vars.add(Symbol(str(var), real=True))
    else:
        deterministic_vars.add(Symbol(str(var), real= True))


# compute_bounds(random_vars,
#                deterministic_vars,
#                2,
#                recurrence_builder,
#                [(Symbol("z0", is_finite=True, positive=True),sympify(0), oo),
#                 (Symbol("x0", is_finite=True, positive=True),sympify(0), oo)],
#                {Symbol("z", real=True): sympify(-1),
#                 Symbol("k", real=True): sympify(0)},
#                {Symbol("z", real=True): sympify(0)})

# To build the supermartingales:

x = Symbol("x")
y = Symbol("y")
k = Symbol("k")

recurrences = {
    x: x-y/5+1, # NOTE: x_{n+1} \leq x_n - y_n + 1
    # y: y+1,
    # y**2: y**2+2*y+1,
    # y**2: y**2+k**2+2*k+2*k*y+3,
    # k*y: k*y+k +y+1,
    y:y+1,
    y**2: y**2+2*y+1,
    y**3: y**3+3*y**2+3*y+1
}
maps1 = get_expectation_maps(recurrences, x, {k})

pass
