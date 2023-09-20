from .actuator import Actuator
from .controller import Controller
from .sensor import Sensor

from sympy import Matrix


class ControlSystem:
    actuator: Actuator
    sensor: Sensor
    controller: Controller

    dynamics: Matrix
    state_symbol: str

    def __init__(self, state_symbol: str = "x"):
        self.state_symbol = state_symbol

    def add_actuator(self, a: Actuator):
        self.actuator = a

    def add_sensor(self, s: Sensor):
        self.sensor = s

    def add_controller(self, c: Controller):
        self.controller = c

    def set_dynamics(self, d: Matrix):
        self.dynamics = d
