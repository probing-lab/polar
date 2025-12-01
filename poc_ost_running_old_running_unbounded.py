from functools import reduce
from typing import List, Tuple
from sympy import Expr, Rational, Symbol, oo, preorder_traversal, solve, sympify
from extension_ost.bound_computation import compute_bounds
from extension_ost.bound_store import BoundStore
from extension_ost.helpers import Expexted
from extension_ost.saturation.saturation_based_bound_computation import compute_bounds_saturation
from inputparser.parser import Parser
from program.condition.true_cond import TrueCond
from program.distribution.distribution import DistributionFunction
from program.transformer import normalize_program
from recurrences.rec_builder import RecBuilder
from termination.martingales.branches.branch_builder import BranchBuilder

program = Parser().parse_file("documentation/loops_ost_extension/running_example_unbounded.prob")
lg = program.loop_guard
print(f"Loop guard: {lg}")
if lg.cop != '>':
    raise Exception(f"unknown cop: {lg.cop}")
assert lg.poly1.is_Symbol,"LHS of loop guard must be a symbol"

loop_var = lg.poly1
loop_guard_rhs = lg.poly2.simplify()
assert loop_guard_rhs.is_number, "RHS of loop guard must simplify to a number"
program.loop_guard = TrueCond()


# Construct normal form so that Polar can analyze it
normalized_program = normalize_program(program)
recurrence_builder = RecBuilder(normalized_program)



# determine the loop variable - for now this must be a single variable
loop_var_initial = recurrence_builder.get_initial_value(loop_var)
assert len(loop_var_initial.free_symbols) == 1, "variable occuring in loop guard must be unspecified at input for now"

# initially assume the loop to be executed at least once, i.e. the loop guard to be true
# TODO

# use the branch builder to get the support
branch_builder = BranchBuilder(normalized_program)
branches = branch_builder.get_branches(loop_var)

# get_maximum_lgc
lgc_lb = 0
lgc_ub = 0
for cond, prob, expr in branches[loop_var]:
    expr = sympify(expr)
    distrs:List[DistributionFunction] = expr.find(DistributionFunction)

    bound_store = BoundStore()
    for distr in distrs:
        bound_store.add_lower_bound(distr, min([ele for support_ele in distr._distribution.get_support() for ele in (support_ele if isinstance(support_ele, Tuple) else [support_ele])]))
        bound_store.add_upper_bound(distr, max([ele for support_ele in distr._distribution.get_support() for ele in (support_ele if isinstance(support_ele, Tuple) else [support_ele])]))

    lbs = max(lb for lb in list(bound_store._get_lower_bounds_for_expression((expr-loop_var).simplify())) if lb.is_number)
    ubs = min(ub for ub in list(bound_store._get_upper_bounds_for_expression((expr-loop_var).simplify())) if ub.is_number)

    lgc_lb = min(lbs, lgc_lb)
    lgc_ub = max(ubs, lgc_ub)




deterministic_vars = set()
random_vars = set()

for var in normalized_program.original_variables:
    if not normalized_program.is_iteration_dependent(var):
        continue
    if normalized_program.is_dependent_vars({var}, normalized_program.dist_variables):
        random_vars.add(Symbol(str(var), real=True))
    else:
        deterministic_vars.add(Symbol(str(var), real=True))


compute_bounds_saturation(random_vars,
               deterministic_vars,
               2,
               {Symbol("x", real=True):1,
                Symbol("z", real=True):1,
                Symbol("k", real=True):1},
               recurrence_builder,
               [(Symbol("x0", is_finite=True, positive=True),sympify(0), oo), 
                (Symbol("y0", is_finite=True),sympify(0), oo),
                (Symbol("z0", is_finite=True),sympify(0), oo)],
               {Symbol("k", real=True):sympify(1), 
                Expexted(Symbol("x", real=True)):-sympify(Rational(13,10))},
               {Symbol("x", real=True): sympify(0),
                Expexted(Symbol("x", real=True)**2):sympify(Rational(22,10))},
               use_minkowski=True,
               num_sparsest_solutions=100,
               keep_non_optimal_martingales=False)
