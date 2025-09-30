from functools import reduce
from sympy import Symbol, oo, solve, sympify
from extension_ost.bound_computation import compute_bounds
from inputparser.parser import Parser
from program.condition.true_cond import TrueCond
from program.transformer import normalize_program
from recurrences.rec_builder import RecBuilder
from termination.martingales.branches.branch_builder import BranchBuilder

program = Parser().parse_file("documentation/loops_ost_extension/running_example.prob")
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
branches = branch_builder.get_branches(Symbol('x'))
pass


deterministic_vars = set()
random_vars = set()

for var in normalized_program.original_variables:
    if not normalized_program.is_iteration_dependent(var):
        continue
    if normalized_program.is_dependent_vars({var}, normalized_program.dist_variables):
        random_vars.add(Symbol(str(var)))
    else:
        deterministic_vars.add(Symbol(str(var)))


compute_bounds(random_vars,
               deterministic_vars,
               2,
               recurrence_builder,
               [(Symbol("x0", is_finite=True, positive=True),sympify(0), oo)],
               {Symbol("x"): sympify(-1), Symbol("k"):sympify(1)},
               {Symbol("x"): sympify(0)})