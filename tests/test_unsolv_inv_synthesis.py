import unittest
import os

from symengine import sympify
from sympy import sympify as ssympify

from cli import ArgumentParser, parse_program, prepare_program
from unsolvable_analysis import UnsolvInvSynthesizer


def get_program(benchmark: str):
    args = ArgumentParser().get_defaults()
    path = os.path.dirname(__file__) + "/unsolvable_benchmarks/" + benchmark
    program = parse_program(path, args.transform_categoricals)
    return prepare_program(program, args)


def get_candidate_vars(vars):
    return [sympify(v) for v in vars]


def synth_inv(vs, deg, program, k=None):
    return UnsolvInvSynthesizer.synth_inv(vs, deg, program, False, False, 0, k)


class TestUnsolvableInvariantSynthesis(unittest.TestCase):
    def test_deg_5(self):
        program = get_program("deg-5.prob")
        vs = get_candidate_vars(["x", "y"])
        solutions = synth_inv(vs, 1, program)
        self.assertIsNotNone(solutions)
        self.assertEqual(len(solutions), 1)
        candidate = solutions[0][0]
        closedform = solutions[0][1]
        self.assertSpecifiedEqual(candidate, "3*x - 2*y")
        self.assertSpecifiedEqual(closedform, "0*n + 0**n")
        solutions = synth_inv(vs, 1, program, k=1)
        self.assertIsNone(solutions)

    def test_fibonaccitrace(self):
        program = get_program("fibonaccitrace.prob")
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
        self.assertSpecifiedEqual(candidate, ssympify("x**2 - 2*x*y*z + y**2 + z**2"))
        self.assertSpecifiedEqual(
            closedform, ssympify("-2*x0*y0*z0 + x0**2 + y0**2 + z0**2")
        )

    def assertSpecifiedEqual(self, general_expr, equal_expr):
        """
        Specifies a given general expression by replacing all symbols starting with "_" by 1.
        Then compares the resulting expression to the second argument.
        """
        general_expr = ssympify(general_expr)
        equal_expr = ssympify(equal_expr)
        substitutions = {}
        for sym in general_expr.free_symbols:
            if str(sym).startswith("_"):
                substitutions[sym] = 1
        specified_expr = general_expr.xreplace(substitutions)
        self.assertTrue((specified_expr - equal_expr).expand() == 0)
