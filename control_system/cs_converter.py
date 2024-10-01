from program import Program, normalize_program
from program.assignment import PolyAssignment
from program.condition import TrueCond
from utils import make_assigns_parallel
from .control_system import ControlSystem
from sympy import Matrix, zeros


class CSConverter:
    control_system: ControlSystem
    is_probabilistic: bool

    def __init__(self, control_system: ControlSystem):
        self.control_system = control_system
        self.is_probabilistic = False
        self.loop_body = []

    def construct_program(self) -> Program:
        self._add_system_dynamics_assigns()
        self._add_controller_assigns()
        self._add_sensor_assigns()
        program = Program(
            [], [], [], [], TrueCond(), self.loop_body, self.is_probabilistic
        )
        return normalize_program(program)

    def _add_system_dynamics_assigns(self):
        state_vars = self.control_system.state_variables
        expressions = self.control_system.dynamics * Matrix(state_vars)
        if self.control_system.actuator is not None:
            acc = self.control_system.actuator
            expressions += acc.effect * Matrix(acc.variables)
        assignments = [
            PolyAssignment.deterministic(v, e) for v, e in zip(state_vars, expressions)
        ]
        assignments = make_assigns_parallel(assignments)
        self.loop_body += assignments

    def _add_controller_assigns(self):
        if self.control_system.controller is None:
            return

        controller = self.control_system.controller
        actuator, state_influence = controller.actuator
        sensor, state_effect, act_effect = controller.sensor

        # Add variables for sensor inputs
        sensor_input_variables = [sv + controller.name for sv in sensor.variables]
        sensor_input_assigns = [
            PolyAssignment.deterministic(iv, sv)
            for iv, sv in zip(sensor_input_variables, sensor.variables)
        ]
        self.loop_body += sensor_input_assigns

        # Add assignments for actuator
        act_expressions = Matrix.zeros(len(actuator.variables), 1)
        if state_influence is not None:
            act_expressions += state_influence * Matrix(controller.state_variables)
        if act_effect is not None:
            act_expressions += act_effect * Matrix(sensor_input_variables)
        act_assigns = [
            PolyAssignment.deterministic(v, e)
            for v, e in zip(actuator.variables, act_expressions)
        ]
        act_assigns = make_assigns_parallel(act_assigns)
        self.loop_body += act_assigns

        # Add assignments for controller state
        if controller.dynamics is not None:
            expressions = controller.dynamics * Matrix(controller.state_variables)
            if state_effect is not None:
                expressions += state_effect * Matrix(sensor_input_variables)
            assigns = [
                PolyAssignment.deterministic(v, e)
                for v, e in zip(controller.state_variables, expressions)
            ]
            assigns = make_assigns_parallel(assigns)
            self.loop_body += assigns

    def _add_sensor_assigns(self):
        if self.control_system.sensor is None:
            return

        sensor = self.control_system.sensor
        state_vars = self.control_system.state_variables
        expressions = sensor.measurement * Matrix(state_vars)
        assignments = [
            PolyAssignment.deterministic(v, e)
            for v, e in zip(sensor.variables, expressions)
        ]
        self.loop_body += assignments
