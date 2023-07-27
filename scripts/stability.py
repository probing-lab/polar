from inputparser import Parser
from program import normalize_program
from recurrences.rec_builder import RecBuilder

from stability_analysis import SymbolicStabilityAnalyzer, NumericStabilityAnalyzer

import time

start = time.time()

source_code = """
# dynamical system parameters
a11 = 0.999
a12 = 0.003002
a21 = 0.002001
a22 = 1.002
b1 = 0.01003
b2 = 0.02003
c1 = 1
c2 = 0.5
period = 0.1

# initialization
x1, x2 = 1, -1
y = c1*x1 + c2*x2
y_measure = y
z, error = 0, 0
setpoint = 1

# control parameters
kp = 10
ki = 0.5

while true:

  # execution of the controller
  error = setpoint - y_measure # input of the controller
  z = z + period*error
  u = kp*error + ki*z

  # execution of dynamical system
  x1, x2 = a11*x1 + a12*x2 + b1*u, a21*x1 + a22*x2 + b2*u
  y = c1*x1 + c2*x2
  g = Normal(0, 1)
  y_measure = y + g

end
"""

program = Parser().parse_string(source_code)
program = normalize_program(program)

rec_builder = RecBuilder(program)
recurrences = rec_builder.get_recurrences("y_measure")

analyzer = NumericStabilityAnalyzer(recurrences)
print(analyzer.is_globally_stable())
print(analyzer.is_unstable())
print(analyzer.is_lyapunov_stable())
print(analyzer.get_equilibrium())

end = time.time()
print(f"{end - start} seconds")
