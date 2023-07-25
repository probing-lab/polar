import unittest

from symengine import sympify

from .common import get_unsolvable_program, assert_specified_proportional
from unsolvable_analysis import UnsolvInvSynthesizer


def get_candidate_vars(variables):
    return [sympify(v) for v in variables]


def synth_inv(vs, deg, program, k=None):
    return UnsolvInvSynthesizer.synth_inv(vs, deg, program, False, False, 0, k)


class TestUnsolvableInvariantSynthesis(unittest.TestCase):
    def test_deg_5(self):
        program = get_unsolvable_program("deg-5.prob")
        vs = get_candidate_vars(["x", "y"])
        solutions = synth_inv(vs, 1, program)
        self.assertIsNotNone(solutions)
        self.assertEqual(len(solutions), 1)
        candidate = solutions[0][0]
        closedform = solutions[0][1]
        assert_specified_proportional(candidate, "3*x - 2*y")
        assert_specified_proportional(closedform, "0*n + 0**n")
        solutions = synth_inv(vs, 1, program, k=1)
        self.assertIsNone(solutions)

    def test_fibonaccitrace(self):
        program = get_unsolvable_program("fibonaccitrace.prob")
        vs = get_candidate_vars(["x", "y", "z"])

        solutions = synth_inv(vs, 1, program)
        self.assertIsNone(solutions)
        solutions = synth_inv(vs, 2, program)
        self.assertIsNone(solutions)

        solutions = synth_inv(vs, 3, program)
        self.assertIsNotNone(solutions)
        self.assertEqual(len(solutions), 1)
        candidate = solutions[0][0]
        closedform = solutions[0][1]
        assert_specified_proportional(candidate, "x**2 - 2*x*y*z + y**2 + z**2")
        assert_specified_proportional(closedform, "-2*x0*y0*z0 + x0**2 + y0**2 + z0**2")

        solutions = synth_inv(vs, 3, program, k=1)
        self.assertIsNotNone(solutions)
        self.assertEqual(len(solutions), 1)
        candidate = solutions[0][0]
        closedform = solutions[0][1]
        assert_specified_proportional(candidate, "x**2 - 2*x*y*z + y**2 + z**2")
        assert_specified_proportional(closedform, "-2*x0*y0*z0 + x0**2 + y0**2 + z0**2")

    def test_genfibonaccitrace(self):
        program = get_unsolvable_program("genfibonaccitrace.prob")
        vs = get_candidate_vars(["x", "y", "z"])

        solutions = synth_inv(vs, 1, program)
        self.assertIsNone(solutions)
        solutions = synth_inv(vs, 2, program)
        self.assertIsNone(solutions)

        solutions = synth_inv(vs, 3, program)
        self.assertIsNotNone(solutions)
        self.assertEqual(len(solutions), 1)
        candidate = solutions[0][0]
        closedform = solutions[0][1]
        assert_specified_proportional(candidate, "4*x**2*y - 2*x*z - y")
        assert_specified_proportional(closedform, "-y0 - 2*x0*z0 + 4*x0**2*y0")

    def test_markov_triples_random(self):
        program = get_unsolvable_program("markov-triples-random.prob")
        vs = get_candidate_vars(["a", "b", "c"])

        solutions = synth_inv(vs, 3, program, k=1)
        self.assertIsNotNone(solutions)
        self.assertEqual(len(solutions), 1)
        candidate = solutions[0][0]
        closedform = solutions[0][1]
        assert_specified_proportional(candidate, "a**2 - 3*a*b*c + b**2 + c**2")
        assert_specified_proportional(closedform, "0")

    def test_markov_triples_toggle(self):
        program = get_unsolvable_program("markov-triples-toggle.prob")
        vs = get_candidate_vars(["a", "b", "c"])

        solutions = synth_inv(vs, 3, program, k=1)
        self.assertIsNotNone(solutions)
        self.assertEqual(len(solutions), 1)
        candidate = solutions[0][0]
        closedform = solutions[0][1]
        assert_specified_proportional(candidate, "a**2 - 3*a*b*c + b**2 + c**2")
        assert_specified_proportional(closedform, "0")

    def test_nagata(self):
        program = get_unsolvable_program("nagata.prob")
        vs = get_candidate_vars(["x", "y", "z"])

        solutions = synth_inv(vs, 2, program, k=1)
        self.assertIsNotNone(solutions)
        self.assertEqual(len(solutions), 1)
        candidate = solutions[0][0]
        closedform = solutions[0][1]

        assert_specified_proportional(candidate, "z + z**2 + x*z + y**2")
        assert_specified_proportional(closedform, "z0 + z0**2 + x0*z0 + y0**2")

    def test_non_lin_markov(self):
        program = get_unsolvable_program("non-lin-markov-1.prob")
        vs = get_candidate_vars(["x", "y"])

        solutions = synth_inv(vs, 1, program)
        self.assertIsNotNone(solutions)
        self.assertEqual(len(solutions), 1)
        candidate = solutions[0][0]
        closedform = solutions[0][1]

        assert_specified_proportional(candidate, "x - y")
        assert_specified_proportional(closedform, "(x0 - y0)*(5/6)**n")

        solutions = synth_inv(vs, 2, program)
        self.assertIsNotNone(solutions)
        self.assertEqual(len(solutions), 2)
        candidate = solutions[1][0]
        closedform = solutions[1][1]

        assert_specified_proportional(candidate, "(x - y)**2")
        assert_specified_proportional(
            closedform, "(13/18)**n*(-2*x0*y0 + x0**2 + y0**2)"
        )

    def test_squares(self):
        program = get_unsolvable_program("squares.prob")
        vs = get_candidate_vars(["x", "y"])

        solutions = synth_inv(vs, 1, program)
        self.assertIsNotNone(solutions)
        self.assertEqual(len(solutions), 1)
        candidate = solutions[0][0]
        closedform = solutions[0][1]

        assert_specified_proportional(candidate, "x + y")
        assert_specified_proportional(
            closedform, "2*2**n*(x0 + y0) + 6*n*(1 - (-1)**(n - 1))"
        )
