from program.assignment import PolyAssignment
from program.mc_comb_finder import MCCombFinder
from recurrences import RecBuilder
from utils import get_unique_var
from symengine.lib.symengine_wrapper import Symbol
from program import Program

class SolvableSynthesizer:
    """
    Synthesizes all solvable loops from an unsolvable loop and returns a list of pairs (inv, program) where inv is the
    list of invariants used for replacing the defective variables with a fresh variable and program is the
    corresponding solvable loop.
    """
    @classmethod
    def synthesize(cls, combination_vars, combination_deg, program: Program, numeric_roots, numeric_croots, numeric_eps):
        candidate, candidate_rec, candidate_coefficients = MCCombFinder.construct_candidate(combination_vars, combination_deg,
                                                                                   program)
        rhs_good_part, good_coeffs = MCCombFinder.construct_inhomogeneous(candidate_rec, program.non_mc_variables,
                                                                 program.variables)
        k, kcandidate = MCCombFinder.construct_homogenous(candidate)
        nice_solutions = MCCombFinder.solve_quadratic_system(candidate, candidate_rec, candidate_coefficients, kcandidate,
                                                    rhs_good_part, good_coeffs, k)
        if len(nice_solutions) == 0:
            return None

        combinations = []
        for solution in nice_solutions:
            s = Symbol(get_unique_var("s"), nonzero=True)
            ans = (k.xreplace(solution)) * s + (rhs_good_part.xreplace(solution))
            combinations.append((s, ans))

        if combinations is None:
            print(f"No combination found with degree {combination_deg}. Try using higher degrees.")
            return program
        else:
            rec_builder = RecBuilder(program)
            solvable_programs = []
            for combination in combinations:
                solvable_loop_body = []
                solvable_loop_variables = []
                for poly_assign in program.loop_body:
                    var = poly_assign.variable
                    if var in program.mc_variables:
                        solvable_loop_body.append(PolyAssignment(var, [rec_builder.get_recurrence_poly(var, [var])], [1]))
                        solvable_loop_variables.append(var)
                comb_var, comb_var_assign = combination[0], combination[1]
                solvable_loop_body.append(PolyAssignment(comb_var, [comb_var_assign], [1]))
                solvable_loop_variables.append(comb_var)

                solvable_program = Program([], solvable_loop_variables, solvable_loop_variables, program.initial,
                                   program.loop_guard, solvable_loop_body, program.is_probabilistic)
                solvable_program.typedefs = program.typedefs

                solvable_programs.append(solvable_program)

        invariants = MCCombFinder.get_invariants(candidate, rec_builder, nice_solutions, rhs_good_part, good_coeffs,
                                                 numeric_roots, numeric_croots, numeric_eps, program, k)
        return invariants, solvable_programs
