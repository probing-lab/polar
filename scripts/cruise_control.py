from inputparser import Parser
from program import normalize_program
from recurrences.rec_builder import RecBuilder

from stability_analysis import SymbolicStabilityAnalyzer, NumericStabilityAnalyzer

file_path = "../benchmarks/control_theory/cruise_control/kill_zero.prob"
program = Parser().parse_file(file_path)
program = normalize_program(program)

rec_builder = RecBuilder(program)
recurrences = rec_builder.get_recurrences("x1", "x2", "x3", "x1**2", "x2**2", "x3**2")

analyzer = NumericStabilityAnalyzer(recurrences)
print(analyzer.is_globally_stable())
print(analyzer.get_rho())
print(analyzer.get_equilibrium())
