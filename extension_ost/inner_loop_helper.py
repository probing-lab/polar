from sympy import sympify
from inputparser import Parser
from program import normalize_program
from recurrences import RecBuilder
from recurrences.solver import RecurrenceSolver
from invariants import InvariantIdeal

program = Parser().parse_file("documentation/test/inner.prob")
# Construct normal form so that Polar can analyze it
program = normalize_program(program)


# Construct and solve recurrences
def get_martingale_for_inner_loop (monomials):
    rec_builder = RecBuilder(program)
    closed_forms = {}
    for monomial in monomials:
        if f"E({monomial})" in closed_forms:
            continue
        # Construct the recurrences describing E(monomial) -> expected value of monomial
        recurrences = rec_builder.get_recurrences(monomial)
        # solve and save the closed-forms (use E(monomial) as the id because the loop is probabilistic)
        closed_forms[f"E({monomial})"] = RecurrenceSolver(recurrences).get(monomial)
    closed_forms={}
    closed_forms[f"E(k1-k)"] = sympify("1")
    closed_forms[f"E(k1**2-k**2)"] = sympify("2*n+1")
    closed_forms[f"E(y1-y)"] = sympify("-1")
    closed_forms[f"E(y1**2-y**2)"] = sympify("-2*y+301") # E(((y+r1)(y+r1)) = E(y^2 + 2r1 y + E(r1^2))
    closed_forms[f"E(y1*k1 - y*k)"] = sympify("y-n-1") #(y+r)*(k+1) = (yk+rk+r+y)-yk = rk+r+y
    # Construct the invariant ideal
    invariant_ideal = InvariantIdeal(closed_forms)
    basis = invariant_ideal.compute_basis()
    return basis
