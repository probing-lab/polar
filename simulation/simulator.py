from typing import Dict, List
from singledispatchmethod import singledispatchmethod
from symengine.lib.symengine_wrapper import Symbol
from program import Program
from program.assignment import Assignment
from program.ifstatem import IfStatem
from .simulation_result import SimulationResult
from progress.bar import Bar


class Simulator:
    """
    Class to simulate a program for a given number of iterations and collect the results.
    """

    iterations: int

    def __init__(self, iterations: int):
        self.iterations = iterations

    def simulate(self, program: Program, goals: List[str], samples: int):
        result = []
        sample_bar = Bar("Computing samples", max=samples)
        for _ in range(samples):
            states = [self.execute(program.initial, {})]
            for _ in range(self.iterations):
                if not program.loop_guard.evaluate(states[-1]):
                    states.append(states[-1].copy())
                else:
                    states.append(self.execute(program.loop_body, states[-1].copy()))
            sample_bar.next()
            result.append(states)
        sample_bar.finish()
        return SimulationResult(result, goals)

    @singledispatchmethod
    def execute(self, program_element, state: Dict[Symbol, float]):
        raise RuntimeError(f"Unknown program element in simulation, {program_element}")

    @execute.register
    def _(self, program_element: list, state: Dict[Symbol, float]):
        for element in program_element:
            state = self.execute(element, state)
        return state

    @execute.register
    def _(self, program_element: IfStatem, state: Dict[Symbol, float]):
        for i in range(len(program_element.conditions)):
            if program_element.conditions[i].evaluate(state):
                return self.execute(program_element.branches[i], state)
        if program_element.else_branch:
            return self.execute(program_element.else_branch, state)

    @execute.register
    def _(self, program_element: Assignment, state: Dict[Symbol, float]):
        return program_element.evaluate(state)
