from control_system import *
from sympy import Matrix

# Setup control system
cc_system = ControlSystem()
cc_system.set_dynamics(
    Matrix([[1, 0.01, 0], [-0.0003, 0.9997, 0.01], [-0.0604, -0.0531, 0.9974]])
)

# Construct and add sensor
sensor = Sensor()
sensor.set_measurement(Matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]]))
sensor.set_fault_probability(0.1)
cc_system.add_sensor(sensor)

# Construct and add actuator
actuator = Actuator()
actuator.set_effect(Matrix([0.0001, 0.0001, 0.0247]))
actuator.set_fault_probability(0.2)
actuator.set_fault_strategy(ActuatorFaultStrategy.ZERO)
cc_system.add_actuator(actuator)

# Construct and add controller
controller = Controller()
sensor_act_effect = Matrix([-872.54, -131.49, -10.097]).T
controller.set_sensor(sensor, actuator_effect=sensor_act_effect)
controller.set_actuator(actuator)
cc_system.add_controller(controller)

converter = CSConverter(cc_system)
program = converter.construct_program()
print(program)
