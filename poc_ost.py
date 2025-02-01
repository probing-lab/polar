from functools import reduce
from typing import Dict
from symengine.lib.symengine_wrapper import sympify
from sympy import Piecewise, solve, symbols
from extension_ost.expectation_map import get_expectation_maps
from extension_ost.helpers import Expexted
from inputparser.parser import Parser
from invariants.invariant_ideal import InvariantIdeal
from program.condition.true_cond import TrueCond
from program.transformer import normalize_program
from recurrences.rec_builder import RecBuilder

program = Parser().parse_file("documentation/test/example_paper_2019.prob")
lg = program.loop_guard
print(f"Loop guard: {lg}")
if lg.cop != '>':
    raise Exception(f"unknown cop: {lg.cop}")
loop_guard = lg.poly1 > lg.poly2
program.loop_guard = TrueCond()
# Construct normal form so that Polar can analyze it
normalized_program = normalize_program(program)

vars = normalize_program.effective_variables

recurrence_builder = RecBuilder(program)

monoms = [sympify('k'),sympify('k**2'),sympify('x**2'), sympify('x*k')]



recurrences = {monom: recurrence_builder.get_recurrence(monom) for monom in monoms}

sols = get_expectation_maps(recurrences)

final_expression1 = sols[0]
# get initial value
monom_subs = {f"E({monom})":monom for monom in monoms}
initial_value_dict = {var: recurrence_builder.get_initial_value(var) for var in vars}
initial_value = final_expression1.subs(monom_subs).subs(initial_value_dict).simplify()

final_expression1= final_expression1 - initial_value
# Use Expected value function of sympy - this allows us to use solve and stuff like this. Unfortunately incompatible with most of polar.
for monom in monoms:
    final_expression1 = final_expression1.subs(f"E({monom})", Expexted(monom))

goal_monom = Expexted(sympify('k**2'))

print(final_expression1.expand().simplify())
print(final_expression1.subs(sympify('k'), sympify('(k-1)')).expand().simplify())

res = solve(final_expression1, goal_monom)
print(res)

res1 = solve (final_expression1.subs(sympify('k'), sympify('(k-1)')).expand().simplify(), goal_monom)
print(res1)
pass