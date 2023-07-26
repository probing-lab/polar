import os
import unittest

from cli import ArgumentParser
from cli.common import prepare_program
from inputparser import parse_program
from symengine.lib.symengine_wrapper import sympify


class AbstractInterpretationTest(unittest.TestCase):
    def test_distribution_support(self):
        benchmark = (
            os.path.dirname(__file__) + "/benchmarks/abstract-interpretation.prob"
        )
        args = ArgumentParser().get_defaults()
        program = parse_program(benchmark, args.transform_categoricals)
        program = prepare_program(program, args)
        self.assertEqual(
            program.get_type(sympify("x")).values, {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
        )
        self.assertEqual(program.get_type(sympify("flip")).values, {0, 1})
        self.assertEqual(program.get_type(sympify("target")).values, {0, 1})


if __name__ == "__main__":
    unittest.main()
