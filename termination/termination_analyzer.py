from typing import Dict, List, Optional, Set, Tuple
from sympy import Expr, Monomial, Poly, Symbol, sympify
from termcolor import colored
from program.assignment.dist_assignment import DistAssignment
from program.condition.atom_cond import Atom
from program.condition.condition import Condition
from program.program import Program
from recurrences.rec_builder import RecBuilder
from recurrences.recurrences import Recurrences
from recurrences.solver.recurrence_solver import RecurrenceSolver
from termination.martingales.bounds.compute_bounds import compute_bounds_of_expr
from termination.martingales.branches.branch_builder import BranchBuilder
from termination.polynomial.polynomial_termination_condition import PolynomialTerminationCondition
from termination.polynomial.termination_witness import TerminationWitness
from termination.smt.smt_formula import SMTFormula
from termination.smt.smt_termination_condition import SMTTerminationCondition
from termination.variance_based.variance_based_termination_analyzer import VarianceBasedTerminationAnalyzer
from utils.expressions import get_monoms, unpack_piecewise


class TerminationAnalyzer:
    @classmethod
    def analyze(cls, normalized_program: Program, loop_guard: Condition, smt=False, amber=False, variance_based=False, exact=False):
        print()
        print(colored("-------------------", "cyan"))
        print(colored("-   Termination   -", "cyan"))
        print(colored("-------------------", "cyan"))
        print()

        if type(loop_guard) != Atom:
            print("At the moment only loop guard consisting of a single condition are supported")
            return
        
        poly, terminates_zero, terminates_negative = cls._normalize_atom(loop_guard)
        
        closed_form_poly = poly.expand().subs(cls._compute_closed_form_of_polynomial(poly.free_symbols, normalized_program))

        if amber:
            # apply amber methodology
            print(normalized_program.variables)
            branches = cls._compute_branches_for_polynomial(list(normalized_program.variables)+[poly], normalized_program)
            print(branches)
            
            bounds = cls._compute_bounds_form_polynomial(poly, branches, normalized_program)
            print(bounds)
        elif smt:
            has_prolog = normalized_program.initial is not None and len(normalized_program.initial) > 0
            formula = SMTTerminationCondition(closed_form_poly, 
                                              terminates_zero, 
                                              terminates_negative, 
                                              has_prolog).get_smt_formula()
            if formula is not None:
                print(formula)
            else:
                print("No formula was found.")
        elif variance_based:
            lc_recurrence = cls._compute_branches_for_polynomial([poly], normalized_program)[poly]
            assert len(lc_recurrence) == 2, "More than two branches exist"
            p1, q1_r = lc_recurrence[0]
            p2, q2_r = lc_recurrence[1]
            assert -0.00001 < p1+p2-1 < 0.00001
            # substract the initial value from the branches
            q1_r = (q1_r - poly).simplify()
            q2_r = (q2_r - poly).simplify()
            # compute closed form poly of q1 and q2
            r = cls._compute_closed_form_of_polynomial([q1_r, q2_r], normalized_program)
            q1 = r[q1_r]
            q2 = r[q2_r]
            analyzer = VarianceBasedTerminationAnalyzer(p1, q1, p2, q2)
            witness = analyzer.compute_bound(exact)
            witness.print()
        else:
            witness = PolynomialTerminationCondition(closed_form_poly, terminates_zero, terminates_negative).get_witness()
            if witness is None:
                print("Program termination could not be determined")
                return
            if witness.is_termination_witness():
                print(colored("Program terminates. Witness found:", "green"))
            else:
                print(colored("Program does not terminate. Witness found:", "green"))
            print(witness)

    @classmethod
    def _get_nondeterministic_branches(cls, branches: Dict[Monomial, List[Tuple[Expr, Expr]]], 
                                  dist_vars: List[Symbol]):
        """Fixpoint computation of the set of nondeterministic vars by looping over all branches"""
        nondeterministic_vars: Set[Symbol] = set(dist_vars)

        old_nondeterministic_vars = set()
        while len(old_nondeterministic_vars) != len(nondeterministic_vars):
            # save old vars
            old_nondeterministic_vars = nondeterministic_vars

            for monom in branches:
                if len(branches[monom])>1:
                    nondeterministic_vars.add(monom)
                    continue
                for prob_expr, eval_expr in branches[monom]:
                    if eval_expr.free_symbols and len(eval_expr.free_symbols & nondeterministic_vars) > 0:
                        nondeterministic_vars.add(monom)
        return nondeterministic_vars
        

    @classmethod
    def _compute_bounds_form_polynomial(cls, poly: Poly, 
                                        branches: Dict[Symbol, List[Tuple[Expr, Expr]]],
                                        program: Program):
        dist_assignments = {}
        poly = Poly(poly)

        for assignment in program.loop_body:
            if isinstance(assignment, DistAssignment):
                assert assignment.variable not in dist_assignments, "Program not in single-assignment form"
                dist_assignments[assignment.variable] = assignment
        
        rec_builder = RecBuilder(program)
        initial_values = rec_builder.get_initial_values(program.variables)
        nondeterministic_vars = cls._get_nondeterministic_branches(branches, dist_assignments.keys())
        symbols = set().union(*[det_monom.free_symbols for det_monom in branches.keys()-nondeterministic_vars])

        closed_forms = cls._compute_closed_form_of_polynomial(symbols, program)

        deterministic_closed_forms = [det_monom.subs(closed_forms) for det_monom in branches.keys()-nondeterministic_vars]
        bounds = cls._compute_bounds_of_expr(poly, branches, dist_assignments, deterministic_closed_forms, initial_values)
        return bounds
    
    @classmethod
    def _compute_bounds_of_expr(cls, poly: any,
                                branches: Dict[Symbol, List[Tuple[Expr, Expr]]],
                                dist_assignments: Dict[Symbol, DistAssignment],
                                closed_forms: Dict[Symbol, Expr],
                                initial_values: Dict[Symbol, Expr]):
        branches = {sympify(b): [(sympify(ex1), sympify(ex2)) for ex1, ex2 in branches[b]] for b in branches}
        dist_assignments = {sympify(s): dist_assignments[s] for s in dist_assignments}
        bounds = compute_bounds_of_expr(poly, branches, dist_assignments, closed_forms, initial_values)
        return bounds

    @classmethod
    def _compute_branches_for_polynomial(cls, polys: List[Poly], program: Program):
        branch_builder = BranchBuilder(program)
        branches:Dict[Symbol, List[Tuple[Expr, Expr]]] = {}

        for poly in polys:
            expanded_poly = poly.expand()
            symbols = expanded_poly.free_symbols

            for symbol in symbols:
                branches.update(branch_builder.get_branches(symbol))
            
        return branches

    @classmethod
    def _compute_closed_form_of_polynomial(cls, symbols: List[Symbol], program: Program):
        recurrence_builder = RecBuilder(program)
        solvers = {}
        closed_forms = {}

        for symbol in symbols:
            symbol1 = symbol
            symbol = sympify(str(symbol))
            if symbol not in solvers:
                recurrences = recurrence_builder.get_recurrences(symbol)
                s = RecurrenceSolver(recurrences)
                solvers.update({sympify(m): s for m in recurrences.monomials})
            closed_forms[symbol1], is_exact = recurrence_builder.get_solution(symbol, solvers)
            if not is_exact:
                print("Only exact closed forms are supported")

        closed_forms = {k: unpack_piecewise(closed_forms[k]) for k in closed_forms}
        return closed_forms

    @classmethod
    def _normalize_atom(cls, atom: Atom) -> Tuple[Poly, bool, bool]:
        # returns a normalized polynomial as first return value.
        # second return value specifies, whether the condition is false for zero
        if atom.cop == ">":
            return atom.poly1 - atom.poly2, True, True
        if atom.cop == "<":
            return atom.poly2 - atom.poly1, True, True
        if atom.cop == ">=":
            return atom.poly1 - atom.poly2, False, True
        if atom.cop == "<=":
            return atom.poly2 - atom.poly1, False, True
        if atom.cop == "==":
            return atom.poly2 - atom.poly1, True, False
        else:
            raise NotImplementedError()
