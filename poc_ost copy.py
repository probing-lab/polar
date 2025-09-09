from functools import reduce
from typing import Dict
from symengine.lib.symengine_wrapper import sympify
from sympy import Piecewise, Symbol, reduce_inequalities, solve, symbols, sympify as sp_sympify
from extension_ost.bound_computation import compute_bounds
from extension_ost.bound_store import BoundStore
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
loop_guard = lg.poly1 - lg.poly2 # <= 0 
program.loop_guard = TrueCond()
# Construct normal form so that Polar can analyze it
normalized_program = normalize_program(program)

recurrence_builder = RecBuilder(normalized_program)

compute_bounds({Symbol("x")},
               {Symbol("k")},
               2,
               recurrence_builder,
               [Symbol("x0", positive=True, is_finite=True)],
               {Symbol("x"):-sympify(1), Symbol("k"):sympify(1)},
               {Symbol("x"): sympify(0)})