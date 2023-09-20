from sympy import Matrix, Expr, sympify
from typing import Tuple
from enum import Enum, auto

from .sensor import Sensor
from .actuator import Actuator

StateEffect = Matrix
StateInfluence = Matrix
ActuatorEffect = Matrix


class ControllerFaultStrategy(Enum):
    SKIP = auto()
    KILL = auto()


class Controller:
    dynamics: Matrix
    state_symbol: str
    sensor: Tuple[Sensor, StateEffect, ActuatorEffect]
    actuator: Tuple[Actuator, StateInfluence]
    fault_probability: Expr
    fault_strategy: ControllerFaultStrategy

    def __init__(self, state_symbol: str = "z"):
        self.state_symbol = state_symbol

    def set_dynamics(self, d: Matrix):
        self.dynamics = d

    def set_sensor(
        self, sensor: Sensor, state_effect: StateEffect, actuator_effect: ActuatorEffect
    ):
        self.sensor = (sensor, state_effect, actuator_effect)

    def set_actuator(self, actuator: Actuator, state_influence: StateInfluence):
        self.actuator = (actuator, state_influence)

    def set_fault_probability(self, p: Expr | float):
        self.fault_probability = sympify(p)

    def set_fault_strategy(self, fs: ControllerFaultStrategy):
        self.fault_strategy = fs
