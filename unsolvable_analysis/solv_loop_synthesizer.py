from program.assignment import PolyAssignment
from .unsolv_inv_synthesizer import UnsolvInvSynthesizer
from recurrences import RecBuilder
from utils import get_unique_var
from symengine.lib.symengine_wrapper import Symbol
from program import Program


class SolvLoopSynthesizer:
    """
    Synthesizes all solvable loops from an unsolvable loop and returns a list of pairs (inv, program) where inv is the
    list of invariants used for replacing the defective variables with a fresh variable and program is the
    corresponding solvable loop.
    """

    @classmethod
    def handle_solvable_loop(cls, program):
        rec_builder = RecBuilder(program)
        solvable_loop_initial = []
        solvable_loop_body = []
        solvable_loop_variables = []
        fresh = dict()
        for poly_assign in program.loop_body:
            var = poly_assign.variable
            if var in program.mc_variables:
                t = Symbol(get_unique_var("t"), nonzero=True)
                solvable_loop_initial.append(
                    PolyAssignment.deterministic(t, rec_builder.get_initial_value(var))
                )
                solvable_loop_body.append(
                    PolyAssignment.deterministic(
                        t, rec_builder.get_recurrence_poly(var, [var])
                    )
                )
                fresh[var] = t
                solvable_loop_variables.append(t)

        for poly_assign in program.loop_body:
            var = poly_assign.variable
            if var in program.mc_variables:
                solvable_loop_initial.append(
                    PolyAssignment.deterministic(var, fresh[var])
                )
                solvable_loop_body.append(PolyAssignment.deterministic(var, fresh[var]))

        return [], [
            Program(
                [],
                solvable_loop_variables,
                solvable_loop_variables,
                solvable_loop_initial,
                program.loop_guard,
                solvable_loop_body,
                program.is_probabilistic,
            )
        ]

    @classmethod
    def handle_unsolvable_loop(
        cls,
        nice_solutions,
        program,
        rhs_good_part,
        combination_vars,
        candidate,
        good_coeffs,
        numeric_roots,
        numeric_croots,
        numeric_eps,
        k,
    ):
        rec_builder = RecBuilder(program)
        combinations = []
        for solution in nice_solutions:
            s = Symbol(get_unique_var("s"), nonzero=True)
            ans = (k.xreplace(solution)) * s + (rhs_good_part.xreplace(solution))
            specialized_candidate = candidate.xreplace(solution)
            initial_candidate = rec_builder.get_initial_value_poly(
                specialized_candidate, combination_vars
            )
            combinations.append((s, ans, initial_candidate))

        solvable_programs = []
        for combination in combinations:
            solvable_loop_initial = []
            solvable_loop_body = []
            solvable_loop_variables = []
            replaced = False
            fresh = dict()
            for poly_assign in program.loop_body:
                var = poly_assign.variable
                if var in program.mc_variables:
                    t = Symbol(get_unique_var("t"), nonzero=True)
                    solvable_loop_initial.append(
                        PolyAssignment.deterministic(
                            t, rec_builder.get_initial_value(var)
                        )
                    )
                    solvable_loop_body.append(
                        PolyAssignment.deterministic(
                            t, rec_builder.get_recurrence_poly(var, [var])
                        )
                    )
                    fresh[var] = t
                    solvable_loop_variables.append(t)
                elif var in combination_vars and not replaced:
                    replaced = True
                    comb_var, comb_var_assign = combination[0], combination[1]
                    solvable_loop_initial.append(
                        PolyAssignment.deterministic(comb_var, combination[2])
                    )
                    solvable_loop_body.append(
                        PolyAssignment.deterministic(comb_var, comb_var_assign)
                    )
                    solvable_loop_variables.append(comb_var)

            for poly_assign in program.loop_body:
                var = poly_assign.variable
                if var in program.mc_variables:
                    solvable_loop_initial.append(
                        PolyAssignment.deterministic(var, fresh[var])
                    )
                    solvable_loop_body.append(
                        PolyAssignment.deterministic(var, fresh[var])
                    )

            solvable_program = Program(
                [],
                solvable_loop_variables,
                solvable_loop_variables,
                solvable_loop_initial,
                program.loop_guard,
                solvable_loop_body,
                program.is_probabilistic,
            )
            solvable_program.typedefs = program.typedefs
            solvable_programs.append(solvable_program)

        invariants = UnsolvInvSynthesizer.get_invariants(
            candidate,
            rec_builder,
            nice_solutions,
            rhs_good_part,
            good_coeffs,
            numeric_roots,
            numeric_croots,
            numeric_eps,
            program,
            k,
        )
        return invariants, solvable_programs

    @classmethod
    def synthesize(
        cls,
        combination_vars,
        combination_deg,
        program: Program,
        numeric_roots,
        numeric_croots,
        numeric_eps,
    ):
        if len(combination_vars) == 0:  # loop is already solvable
            return cls.handle_solvable_loop(program)
        (
            candidate,
            candidate_rec,
            candidate_coefficients,
        ) = UnsolvInvSynthesizer.construct_candidate(
            combination_vars, combination_deg, program
        )
        rhs_good_part, good_coeffs = UnsolvInvSynthesizer.construct_inhomogeneous(
            candidate_rec, program.non_mc_variables, program.variables
        )
        k, kcandidate = UnsolvInvSynthesizer.construct_homogenous(candidate)
        nice_solutions = UnsolvInvSynthesizer.solve_quadratic_system(
            candidate,
            candidate_rec,
            candidate_coefficients,
            kcandidate,
            rhs_good_part,
            good_coeffs,
            k,
        )

        if len(nice_solutions) == 0:  # no combination found
            return cls.handle_solvable_loop(program)
        else:
            return cls.handle_unsolvable_loop(
                nice_solutions,
                program,
                rhs_good_part,
                combination_vars,
                candidate,
                good_coeffs,
                numeric_roots,
                numeric_croots,
                numeric_eps,
                k,
            )
