from control_system import *
from sympy import Matrix


ball_beam_system = ControlSystem()

# Setup control system
ball_beam_system.set_dynamics(Matrix([[1, 0.015, 0.0003], [0, 1, 0.045], [0, 0, 1]]))

# Construct and add sensor
sensor = Sensor()
sensor.set_measurement(Matrix([[0.5, 0, 0], [0, 0, 0.25]]))
sensor.set_fault_probability(0.2)
ball_beam_system.add_sensor(sensor)

# Construct and add actuator
actuator = Actuator()
actuator.set_effect(Matrix([[2.9e-5, 0.0058, 0.256]]).T)
actuator.set_fault_probability(0.3)
actuator.set_fault_strategy(ActuatorFaultStrategy.HOLD)
ball_beam_system.add_actuator(actuator)

# Construct and add controller
controller = Controller()
controller.set_dynamics(Matrix([[1, 0], [0, 0.9685]]))
sensor_state_effect = Matrix([[0.025, 0], [-0.2608, 0]])
sensor_act_effect = Matrix([-2.43, -3])
controller.set_sensor(sensor, sensor_state_effect, sensor_act_effect)
state_influence = Matrix([-0.108, -0.2608])
controller.set_actuator(actuator, state_influence)
controller.set_fault_probability(0.5)
ball_beam_system.add_controller(controller)
