from functools import reduce
from sympy import Symbol, oo, sympify
from extension_ost.bound_computation import compute_bounds
from inputparser.parser import Parser
from program.condition.true_cond import TrueCond
from program.transformer import normalize_program
from recurrences.rec_builder import RecBuilder

program = Parser().parse_file("documentation/test/example_paper_2019.prob")
lg = program.loop_guard
print(f"Loop guard: {lg}")
if lg.cop != '>':
    raise Exception(f"unknown cop: {lg.cop}")
loop_guard = lg.poly1 - lg.poly2 # <= 0 
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
        random_vars.add(Symbol(str(var)))
    else:
        deterministic_vars.add(Symbol(str(var)))

# compute_bounds({Symbol("x")},
#                {Symbol("k")},
#                2,
#                recurrence_builder,
#                [(Symbol("x0", is_finite=True, positive=True),sympify(1), oo)],
#                {Symbol("x"): sympify(0), Symbol("k"):sympify(1), Symbol("k")*Symbol("x"):sympify(0)},
#                {Symbol("x"): sympify(1)})

compute_bounds(random_vars,
               deterministic_vars,
               3,
               recurrence_builder,
               [(Symbol("x0", is_finite=True, positive=True),sympify(0), oo)],
               {Symbol("x"): sympify(-1), Symbol("k"):sympify(1)},
               {Symbol("x"): sympify(0)})