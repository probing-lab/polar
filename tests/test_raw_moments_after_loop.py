import glob
import os
import unittest

from cli.argument_parser import ArgumentParser
from cli.common import (
    get_moment_given_termination,
    transform_to_after_loop,
)
from program import normalize_program
from inputparser import parse_program
from recurrences import RecBuilder
from utils import unpack_piecewise
from tests.common import get_test_specs

from sympy import sympify as sympy_sympify
from symengine import sympify as symengine_sympify


def create_raw_moment_after_loop_test(benchmark, monom, general_form):
    monom = symengine_sympify(
        monom
    )  # moment calculation function expect symengine format
    general_form = sympy_sympify(
        general_form
    )  # final comparison is done in sympy format

    def test(self: RawMomentsAfterLoopTest):
        solution, is_exact = get_raw_moment_after_loop(benchmark, monom)
        self.assertTrue(is_exact)
        self.assertEqual(general_form.expand(), unpack_piecewise(solution).expand())

    return test


def get_raw_moment_after_loop(benchmark, monom):
    args = ArgumentParser().get_defaults()
    program = parse_program(benchmark, args.transform_categoricals)
    program = normalize_program(program, args)
    rec_builder = RecBuilder(program)
    moment, is_exact = get_moment_given_termination(
        monom, {}, rec_builder, args, program
    )
    return transform_to_after_loop(moment), is_exact


class RawMomentsAfterLoopTest(unittest.TestCase):
    pass


benchmarks = glob.glob(os.path.dirname(__file__) + "/benchmarks/*")
for benchmark in benchmarks:
    benchmark_name = os.path.basename(benchmark).replace(".prob", "")
    specs = get_test_specs(benchmark, "raw_after_loop")
    for spec in specs:
        test_case = create_raw_moment_after_loop_test(benchmark, spec[0], spec[1])
        monom_id = spec[0].replace("*", "")
        test_name = f"test_raw_moment_after_loop_{benchmark_name}_{monom_id}"
        setattr(RawMomentsAfterLoopTest, test_name, test_case)


if __name__ == "__main__":
    unittest.main()
