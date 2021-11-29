import glob
import os
import unittest

from cli import ArgumentParser
from cli.common import prepare_program, parse_program
from recurrences import RecBuilder
from recurrences.solver import RecurrenceSolver
from utils import unpack_piecewise
from tests.common import get_test_specs

from sympy import Symbol, sympify


def create_raw_moment_test(benchmark, monom, initial_value, general_form):
    monom = sympify(monom)
    n = Symbol("n", integer=True)
    initial_value = sympify(initial_value).xreplace({Symbol("n"): n})
    general_form = sympify(general_form).xreplace({Symbol("n"): n})

    def test(self: RawMomentsTest):
        solution, is_exact = get_raw_moment(benchmark, monom)
        self.assertTrue(is_exact)
        self.assertEqual(initial_value.expand(), solution.subs({n: 0}))
        self.assertEqual(general_form.expand(), unpack_piecewise(solution).expand())
    return test


def get_raw_moment(benchmark, monom):
    args = ArgumentParser().get_defaults()
    program = parse_program(benchmark, args.transform_categoricals)
    program = prepare_program(program, args)
    rec_builder = RecBuilder(program)
    recurrences = rec_builder.get_recurrences(monom)
    solver = RecurrenceSolver(recurrences, False, False, 0)
    moment = solver.get(monom)
    return moment, solver.is_exact


class RawMomentsTest(unittest.TestCase):
    pass


benchmarks = glob.glob(os.path.dirname(__file__) + "/benchmarks/*")
for benchmark in benchmarks:
    benchmark_name = os.path.basename(benchmark).replace(".prob", "")
    specs = get_test_specs(benchmark, "raw")
    for spec in specs:
        test_case = create_raw_moment_test(benchmark, spec[0], spec[1], spec[2])
        monom_id = spec[0].replace("*", "")
        test_name = f"test_raw_moment_{benchmark_name}_{monom_id}"
        setattr(RawMomentsTest, test_name, test_case)


if __name__ == '__main__':
    unittest.main()
