from functools import reduce
from typing import List, Tuple
from sympy import Expr, Rational, Symbol, oo, preorder_traversal, solve, sympify
from extension_ost.bound_computation import compute_bounds
from extension_ost.bound_store import BoundStore
from extension_ost.expectation_map import get_expectation_maps
from inputparser.parser import Parser
from program.condition.true_cond import TrueCond
from program.distribution.distribution import DistributionFunction
from program.transformer import normalize_program
from recurrences.rec_builder import RecBuilder
from termination.martingales.branches.branch_builder import BranchBuilder


x = Symbol("x", real=True)
k = Symbol("k", real=True)
z = Symbol("z", real=True)


recurrences = {
    x: x-k/5-1/5, # recurrence is actually an inequality (must be careful about signs!)
    k:k+1,
    k**2: k**2+2*k+1
}
maps1 = get_expectation_maps(recurrences, k, set())

print(maps1)