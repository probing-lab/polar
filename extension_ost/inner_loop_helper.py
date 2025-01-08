from inputparser import Parser
from program import normalize_program
from recurrences import RecBuilder
from recurrences.solver import RecurrenceSolver
from invariants import InvariantIdeal

program = Parser().parse_file("documentation/test/inner.prob")
# Construct normal form so that Polar can analyze it
program = normalize_program(program)


# Construct and solve recurrences
def     get_martingale_for_inner_loop (monomials):
    rec_builder = RecBuilder(program)
    closed_forms = {}
    for monomial in monomials:
        if f"E({monomial})" in closed_forms:
            continue
        # Construct the recurrences describing E(monomial) -> expected value of monomial
        recurrences = rec_builder.get_recurrences(monomial)
        # solve and save the closed-forms (use E(monomial) as the id because the loop is probabilistic)
        closed_forms[f"E({monomial})"] = RecurrenceSolver(recurrences).get(monomial)

    # Construct the invariant ideal
    invariant_ideal = InvariantIdeal(closed_forms)
    basis = invariant_ideal.compute_basis()
    return basis
