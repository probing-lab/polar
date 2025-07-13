from functools import reduce
from typing import Dict
from symengine.lib.symengine_wrapper import sympify
from sympy import Piecewise, Symbol, reduce_inequalities, solve, symbols, sympify as sp_sympify
from extension_ost.bound_store import BoundStore
from extension_ost.expectation_map import get_expectation_maps
from extension_ost.helpers import Expexted
from inputparser.parser import Parser
from invariants.invariant_ideal import InvariantIdeal
from program.condition.true_cond import TrueCond
from program.transformer import normalize_program
from recurrences.rec_builder import RecBuilder

test = Symbol("test", real=True)
test1 = sympify("a<2")

program = Parser().parse_file("documentation/test/example_paper_2019.prob")
lg = program.loop_guard
print(f"Loop guard: {lg}")
if lg.cop != '>':
    raise Exception(f"unknown cop: {lg.cop}")
loop_guard = lg.poly1 - lg.poly2 # > 0 
program.loop_guard = TrueCond()
# Construct normal form so that Polar can analyze it
normalized_program = normalize_program(program)

vars = normalized_program.effective_variables

recurrence_builder = RecBuilder(program)

monoms = [sympify('k'), sympify('x')]


upper_bounds = {}
lower_bounds = {Symbol('k'): sympify(1), Symbol('x0', is_finite=True):1}


recurrences = {monom: recurrence_builder.get_recurrence(monom) for monom in monoms}
print(recurrences)

goal_monom = sympify('k')
sols = get_expectation_maps(recurrences, goal_monom, {sympify('k')})
print(sols)
final_expression1 = sols[0]
# get initial value
monom_subs = {f"E({monom})":monom for monom in monoms}
initial_value_dict = {var: recurrence_builder.get_initial_value(var) for var in vars}
initial_value = final_expression1.subs(monom_subs).subs(initial_value_dict).simplify()

final_expression1= final_expression1 - initial_value
# Use Expected value function - this allows us to use solve and stuff like this. Unfortunately incompatible with most of polar.
for monom in monoms:
    final_expression1 = final_expression1.subs(f"E({monom})", Expexted(monom))

print(final_expression1)
goal_monom = Expexted(sympify('k'))

expression_solved = solve(final_expression1, goal_monom)[0]
expression_solved = expression_solved.subs(Symbol("x0"), Symbol("x0", is_finite=True))
print(expression_solved)

bound_store = BoundStore()
bound_store.upper_bounds = upper_bounds 
bound_store.upper_bounds[Symbol("x")]= sympify(0)
bound_store.lower_bounds = lower_bounds 
bound_store.lower_bounds[Symbol("x")]= sympify(-1)
bound_store.add_initial(Symbol('x0', is_finite=True))

upper_bound = bound_store._get_upper_bound_for_expression(expression_solved)
print(upper_bound)

bound_store = BoundStore()
bound_store.upper_bounds = upper_bounds 
bound_store.upper_bounds[Symbol("x")]= sympify(1)
bound_store.lower_bounds = lower_bounds 
bound_store.lower_bounds[Symbol("x")]= sympify(0)
bound_store.add_initial(Symbol('x0', is_finite=True))

print("================")
print(expression_solved)
expression_solved = expression_solved.subs(sympify('k'), sympify('(k-1)').expand().simplify())
print(expression_solved)

upper_bound = bound_store._get_upper_bound_for_expression(expression_solved.subs(sympify('k'), sympify('(k-1)').expand().simplify()))
print(upper_bound)

# print(final_expression1.expand().simplify())
# print(final_expression1.subs(sympify('k'), sympify('(k-1)')).expand().simplify())

# res = solve(final_expression1, goal_monom)
# print(res)

# res1 = solve (final_expression1.subs(sympify('k'), sympify('(k-1)')).expand().simplify(), goal_monom)
# print(res1)
pass