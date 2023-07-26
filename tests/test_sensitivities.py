import glob
import os
import unittest

from tests.test_raw_moments import get_raw_moment
from program import normalize_program
from inputparser import parse_program
from recurrences import DiffRecBuilder
from recurrences.solver import RecurrenceSolver
from utils import unpack_piecewise
from tests.common import get_test_specs
from symengine import sympify as symengify
from sympy import Symbol, sympify
import settings


def create_sensitivity_test(
    benchmark, monom, param, initial_value, general_form, diff=False
):
    monom = symengify(monom)
    param = symengify(param)
    n = Symbol("n", integer=True)
    initial_value = sympify(initial_value).xreplace({Symbol("n"): n})
    general_form = sympify(general_form).xreplace({Symbol("n"): n})

    def test(self: SensitivitiesTest):
        if diff:
            # differentiate closed-form
            solution, is_exact = get_sensitivity_diff(benchmark, monom, param)
        else:
            # Use sensitivity recurrences
            solution, is_exact = get_sensitivity(benchmark, monom, param)
        self.assertTrue(is_exact)
        self.assertEqual(initial_value.expand(), solution.subs({n: 0}))
        self.assertEqual(
            general_form.nsimplify().expand(),
            unpack_piecewise(solution).nsimplify().expand(),
        )

    return test


def get_sensitivity(benchmark, monom, param):
    settings.exact_func_moments = True
    program = parse_program(benchmark)
    program = normalize_program(program)
    diff_rec_builder = DiffRecBuilder(program, param)
    recurrences = diff_rec_builder.get_recurrences(monom)
    solver = RecurrenceSolver(recurrences, False, False, 0)
    diff_monom = diff_rec_builder.delta * monom
    sensitivity = solver.get(diff_monom)
    return sensitivity, solver.is_exact


def get_sensitivity_diff(benchmark, monom, param):
    moment, is_exact = get_raw_moment(benchmark, monom)
    return moment.diff(sympify(param)).simplify(), is_exact


class SensitivitiesTest(unittest.TestCase):
    pass


benchmarks = glob.glob(os.path.dirname(__file__) + "/benchmarks/*")
for benchmark in benchmarks:
    benchmark_name = os.path.basename(benchmark).replace(".prob", "")
    sens_specs = get_test_specs(benchmark, "sens")
    sens_diff_specs = get_test_specs(benchmark, "sens-diff")
    for spec in sens_specs:
        test_case = create_sensitivity_test(
            benchmark, spec[0], spec[1], spec[2], spec[3], diff=False
        )
        monom_id = spec[0].replace("*", "")
        param_id = spec[1]
        test_name = f"test_sensitivity_{benchmark_name}_{monom_id}_{param_id}"
        setattr(SensitivitiesTest, test_name, test_case)
    for spec in sens_diff_specs:
        test_case = create_sensitivity_test(
            benchmark, spec[0], spec[1], spec[2], spec[3], diff=True
        )
        monom_id = spec[0].replace("*", "")
        param_id = spec[1]
        test_name = f"test_sensitivity_diff_{benchmark_name}_{monom_id}_{param_id}"
        setattr(SensitivitiesTest, test_name, test_case)


if __name__ == "__main__":
    unittest.main()
