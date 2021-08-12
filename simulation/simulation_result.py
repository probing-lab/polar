import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib
from matplotlib.lines import Line2D

from typing import Dict, List
from statistics import mean
from symengine.lib.symengine_wrapper import sympify, Expr, Piecewise
from sympy import sympify as symsym, re

State = Dict[Expr, float]
Run = List[State]


class SimulationResult:
    """
    Provides the functionality to compute statistics for and plot the result of simulating a program.
    """

    samples: List[Run]
    goals: List[Expr]

    def __init__(self, samples: List[Run], goals: List):
        self.samples = samples
        self.goals = [sympify(g) for g in goals]
        self.__preprocess_samples__()

    def __preprocess_samples__(self):
        new_samples = []
        for run in self.samples:
            new_run = []
            for state in run:
                state = {sympify(k): v for k, v in state.items()}
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

    def get_prepared_data(self, goal):
        goal = sympify(goal)
        data = []
        for run in self.samples:
            run_data = []
            for state in run:
                run_data.append(state[goal])
            data.append(run_data)

        return np.array(data).T

    def plot_runs(self, goal, first_moment=None, second_moment=None, yscale="linear", file_name="plot.pdf"):
        fig, ax = plt.subplots()
        goal = sympify(goal)
        plt.ylabel("$\mathbb{R}$", rotation=0)
        ax.set_yscale(yscale)
        plt.xlabel("n")
        store = [[] for _ in range(len(self.samples[0]))]
        labels = []
        for run in self.samples:
            data = [state[goal] for state in run]
            for i in range(len(data)):
                store[i].append(data[i])
            ax.plot(range(len(run)), data, linewidth=1, color="grey", alpha=0.1)
        labels.append(Line2D([0], [0], label="Samples", color="grey"))

        def eval(n, exact):
            result = exact.xreplace({symsym("n"): n})
            return float(re(result.expand()))

        xs = np.linspace(0, len(self.samples[0]), len(self.samples[0]) * 4)

        if first_moment:
            data = [eval(x, first_moment) for x in xs]
            ax.plot(xs, data, color="red", linewidth=2)
            labels.append(Line2D([0], [0], label="$\mathbb{E}(" + str(goal) + "_n)$", color="red"))

        if first_moment and second_moment:
            variance = second_moment - (first_moment ** 2)
            std = variance ** (1 / 2)

            data = [eval(x, first_moment + 2 * std) for x in xs]
            ax.plot(xs, data, ":", color="red", linewidth=1.5)

            data = [eval(x, first_moment - 2 * std) for x in xs]
            ax.plot(xs, data, ":", color="red", linewidth=1.5)
            labels.append(Line2D([0], [0], linestyle=":", label="$\pm 2 Std(" + str(goal) + "_n)$", color='red'))

        ax.legend(handles=labels)
        plt.savefig(file_name)
        plt.show()

    def plot_states_animated(self, goal, first_moment=None, second_moment=None):
        goal = sympify(goal)
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
        description = f"[{goal.args[1]}]" if isinstance(goal, Piecewise) else str(goal)
        plt.xlabel(f"Empirical distribution of {description}")
        plt.ylabel("Counts")
        plt.show()
