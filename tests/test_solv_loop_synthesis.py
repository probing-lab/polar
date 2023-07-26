import unittest

from symengine import sympify
from sympy import sympify as ssympify

from recurrences import RecBuilder
from unsolvable_analysis import SolvLoopSynthesizer

from .common import get_unsolvable_program, assert_specified_proportional


def get_candidate_vars(variables):
    return [sympify(v) for v in variables]


def synth_loop(vs, deg, program):
    return SolvLoopSynthesizer.synth_loop(vs, deg, program)


def get_recurrence(program, monom, monom_alias=None):
    monom = ssympify(monom)
    rec_builder = RecBuilder(program)
    recurrences = rec_builder.get_recurrences(monom)
    init_val = recurrences.init_values_dict[monom]
    rec = recurrences.recurrence_dict[monom]
    if monom_alias is not None:
        monom_alias = ssympify(monom_alias)
        rec = rec.xreplace({monom: monom_alias})
    return init_val, rec


def get_combination_var(program):
    for var in program.variables:
        if str(var).startswith("_s"):
            return var
    return None


class TestSolvableLoopSynthesis(unittest.TestCase):
    def test_solvable_loop(self):
        program = get_unsolvable_program("solvable-2dwalk.prob")
        vs = []
        _, synth_programs = synth_loop(vs, 1, program)
        self.assertEqual(len(synth_programs), 1)
        synth_program = synth_programs[0]
        x_init, x_rec = get_recurrence(synth_program, "x")
        assert_specified_proportional(x_init, 0)
        assert_specified_proportional(x_rec, "x")
        y_init, y_rec = get_recurrence(synth_program, "y")
        assert_specified_proportional(y_init, 0)
        assert_specified_proportional(y_rec, "y")

    def test_squares(self):
        program = get_unsolvable_program("squares.prob")
        vs = get_candidate_vars(["x", "y"])
        _, synth_programs = synth_loop(vs, 1, program)
        self.assertEqual(len(synth_programs), 1)
        synth_program = synth_programs[0]
        comb_var = get_combination_var(synth_program)
        self.assertIsNotNone(comb_var)
        comb_var_init, comb_var_rec = get_recurrence(synth_program, comb_var, "s")
        assert_specified_proportional(comb_var_init, "x0 + y0")
        assert_specified_proportional(comb_var_rec, "2*s - z + 1")
        z_init, z_rec = get_recurrence(synth_program, "z")
        assert_specified_proportional(z_init, 0)
        assert_specified_proportional(z_rec, "1 - z")

    def test_non_lin_markov(self):
        program = get_unsolvable_program("non-lin-markov-1.prob")
        vs = get_candidate_vars(["x", "y"])
        _, synth_programs = synth_loop(vs, 1, program)
        self.assertEqual(len(synth_programs), 1)
        synth_program = synth_programs[0]
        comb_var = get_combination_var(synth_program)
        self.assertIsNotNone(comb_var)
        comb_var_init, comb_var_rec = get_recurrence(synth_program, comb_var, "s")
        assert_specified_proportional(comb_var_init, "x0 - y0")
        assert_specified_proportional(comb_var_rec, "(5/6)*s")
        z_init, z_rec = get_recurrence(synth_program, "z")
        assert_specified_proportional(z_init, "z0")
        assert_specified_proportional(z_rec, "1/2")
