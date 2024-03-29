import numpy as np
from typing import Dict, List
from statistics import mean
from symengine.lib.symengine_wrapper import sympify, Expr

State = Dict[Expr, float]
Run = List[State]


class SimulationResult:
    """
    Provides the functionality to compute statistics for the result of simulating a program.
    """

    samples: List[Run]
    goals: List[Expr]

    def __init__(self, samples: List[Run], goals: List):
        self.samples = samples
        self.goals = [sympify(g) for g in goals]
        self._preprocess_samples()

    def _preprocess_samples(self):
        new_samples = []
        for run in self.samples:
            new_run = []
            for state in run:
                state = {sympify(k): v for k, v in state.items()}
                goal_values = {g: self._goal_to_float(g, state) for g in self.goals}
                state.update(goal_values)
                new_run.append(state)
            new_samples.append(new_run)
        self.samples = new_samples

    def _goal_to_float(self, goal, state):
        result = sympify(goal).subs(state)
        if not result.is_Number:
            return float("nan")
        return float(result)

    def get_average_goals(self, iteration=-1):
        result = {}
        for goal in self.goals:
            result[goal] = mean([run[iteration][goal] for run in self.samples])
        return result

    def get_prepared_data(self, goal):
        goal = sympify(goal)
        data = []
        for run in self.samples:
            run_data = []
            for state in run:
                run_data.append(state[goal])
            data.append(run_data)

        return np.array(data).T
