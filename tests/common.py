from program import normalize_program
from inputparser import parse_program
import os
from sympy import sympify


def get_test_specs(filename, spec_id):
    specs = []
    starts_with = "#test: " + spec_id + ";"
    with open(filename, "r") as file:
        for line in file:
            if line.startswith(starts_with):
                line = line[len(starts_with) :]
                spec = [d.strip() for d in line.split(";")]
                specs.append(spec)
    return specs


def get_unsolvable_program(benchmark: str):
    path = os.path.dirname(__file__) + "/unsolvable_benchmarks/" + benchmark
    program = parse_program(path)
    return normalize_program(program)


def assert_specified_proportional(general_expr, equal_expr):
    """
    Specifies a given general expression by replacing all symbols starting with "_" by 1.
    Then compares the resulting expression to the second argument.
    """
    general_expr = sympify(general_expr)
    equal_expr = sympify(equal_expr)
    substitutions = {}
    for sym in general_expr.free_symbols:
        if str(sym).startswith("_"):
            substitutions[sym] = 1
        if str(sym) == "n":
            substitutions[sym] = sympify("n")
    specified_expr = general_expr.xreplace(substitutions)
    if (specified_expr - equal_expr).expand().is_zero:
        return
    proportion = (specified_expr / equal_expr).simplify()
    if not proportion.is_constant():
        raise AssertionError(
            f"Specified expression {specified_expr} is not proportional to {equal_expr}"
        )
