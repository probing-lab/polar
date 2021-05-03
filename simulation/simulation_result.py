import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib

from typing import Dict, List
from statistics import mean
from symengine.lib.symengine_wrapper import sympify

State = Dict[str, float]
Run = List[State]


class SimulationResult:
    """
    Provides the functionality to compute statistics for and plot the result of simulating a program.
    """

    samples: List[Run]
    goals: List[str]

    def __init__(self, samples: List[Run], goals: List[str]):
        self.samples = samples
        self.goals = goals
        self.__preprocess_samples__()

    def __preprocess_samples__(self):
        new_samples = []
        for run in self.samples:
            new_run = []
            for state in run:
                state = {str(k): v for k, v in state.items()}
                goal_values = {g: float(sympify(g).subs(state)) for g in self.goals}
                state.update(goal_values)
                new_run.append(state)
            new_samples.append(new_run)
        self.samples = new_samples

    def get_average_goals(self, iteration=-1):
        result = {}
        for goal in self.goals:
            result[goal] = mean([run[iteration][goal] for run in self.samples])
        return result

    def get_prepared_data(self, goal: str):
        data = []
        for run in self.samples:
            run_data = []
            for state in run:
                run_data.append(state[goal])
            data.append(run_data)

        return np.array(data).T

    def plot_animated(self, goal: str):
        matplotlib.use("TkAgg")
        data = self.get_prepared_data(goal)
        number_iter, number_samples = data.shape
        HIST_BINS = np.linspace(data.min(), data.max(), 100)

        def prepare_animation(bar_container):
            def animate(frame_number):
                n, _ = np.histogram(data[frame_number], HIST_BINS)
                for count, rect in zip(n, bar_container.patches):
                    rect.set_height(count)
                return bar_container.patches
            return animate

        fig, ax = plt.subplots()
        _, _, bar_container = ax.hist(data[0], HIST_BINS, lw=1, ec="yellow", fc="blue", alpha=0.5)
        ax.set_ylim(top=number_samples/2)
        interval = 30000 / number_iter
        ani = animation.FuncAnimation(fig, func=prepare_animation(bar_container), interval=interval, frames=number_iter, repeat=False)
        plt.xlabel(f"Empirical distribution of {goal}")
        plt.ylabel("Counts")
        plt.show()
