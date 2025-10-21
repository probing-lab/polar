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

program = Parser().parse_file("documentation/loops_ost_extension/nested_loops/loop1/different_version.prob")
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

r = recurrence_builder.get_recurrence(Symbol("x", real=True)*Symbol("k", real=True))

compute_bounds(random_vars,
               deterministic_vars,
               2,
               recurrence_builder,
               [(Symbol("z0", is_finite=True, positive=True),sympify(0), oo),
                (Symbol("x0", is_finite=True, positive=True),sympify(0), oo)],
               {Symbol("k", real=True): sympify(0)},
               {Symbol("z", real=True): sympify(0)})

exit(0)
# To build the supermartingales:

x = Symbol("x", real=True)
k = Symbol("k", real=True)
z = Symbol("z", real=True)

print("x**2: ", recurrence_builder.get_recurrence(x**2))
print("(x-2/5z)**2: ", recurrence_builder.get_recurrence((x-2/5*z)**2))
print("z: ", recurrence_builder.get_recurrence(z))
print("z**2: ", recurrence_builder.get_recurrence(z**2))

print((recurrence_builder.get_recurrence((x-2/5*z)**2)-(x-2/5*z)**2).expand().simplify())

A = Rational(1,1)
B = Rational(1,1)
C = Rational(48,25)
D = -Rational(2,25)

martingale = A*x**2+B*(x-Rational(2,5)*z)**2+C*z+D*z**2
martingale_exp = (A*recurrence_builder.get_recurrence(x**2)
                  +B*recurrence_builder.get_recurrence((x-Rational(2,5)*z)**2)
                  +C*recurrence_builder.get_recurrence(z)
                  +D*recurrence_builder.get_recurrence(z**2))

print((martingale_exp-martingale).expand().simplify())
print(martingale)

print("==========================")

A = Rational(0,1)
B = Rational(1,1)
C = Rational(24,25)
D = Rational(0,1)

martingale = A*x**2+B*(x-Rational(1,5)*z)**2+C*z+D*z**2
martingale_exp = (A*recurrence_builder.get_recurrence(x**2)
                  +B*recurrence_builder.get_recurrence((x-Rational(1,5)*z)**2)
                  +C*recurrence_builder.get_recurrence(z)
                  +D*recurrence_builder.get_recurrence(z**2))

print((martingale_exp-martingale).expand().simplify())
print(martingale)
print(martingale.expand())


recurrences = {
    x: x-k/5+1, # NOTE: x_{n+1} \leq x_n - y_n + 1
    x**2: x**2-x*k/5+k+2*x+1,

    k*x:((k+1)*(x+1)-(k+1)/5+(x+1)-1/5).expand().simplify(),  
    k:k+1,
    k**2: k**2+2*k+1
}
maps1 = get_expectation_maps(recurrences, k, {k})



martingale_exp = (recurrences[x**2]+(recurrences[x]-2/5*recurrences[k])**2-2/25*recurrences[k**2]+98/25*recurrences[k])
