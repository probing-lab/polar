import numpy as np
from symengine.lib.symengine_wrapper import sympify, Piecewise
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib
from matplotlib.lines import Line2D

from .plot import Plot
from simulation import SimulationResult
from utils import eval_re


class StatesPlot(Plot):

    def __init__(self, simulation_result: SimulationResult, goal, anim_time, max_y=None, first_moment=None,
                 second_moment=None, is_probabilistic=True):
        self.simulation_result = simulation_result
        self.max_y = max_y
        self.goal = goal
        self.anim_time = anim_time
        self.first_moment = first_moment
        self.second_moment = second_moment
        self.is_probabilistic = is_probabilistic
        self.plt = None
        self.ani = None
        self.fps = -1
        self.__build__()

    def __build__(self):
        goal = sympify(self.goal)
        matplotlib.use("TkAgg")
        data = self.simulation_result.get_prepared_data(goal)
        number_iter, number_samples = data.shape
        HIST_BINS = np.linspace(data.min(), data.max(), 100)
        labels = []
        frames_factor = 1
        expectations = None
        if self.first_moment is not None:
            expectations = [float(eval_re(n, self.first_moment)) for n in range(number_iter)]
        stds = None
        if self.is_probabilistic and self.second_moment is not None:
            second_moments = [float(eval_re(n, self.second_moment)) for n in range(number_iter)]
            stds = [(second_moments[n] - (expectations[n] ** 2)) ** (1 / 2) for n in range(number_iter)]
            stds = [(expectations[n] - 2 * stds[n], expectations[n] + 2 * stds[n]) for n in range(number_iter)]

        def prepare_animation(bar_container, expectation_line, std_line_0, std_line_1):
            def animate(frame_number):
                frame_number = int(frames_factor * frame_number)
                n, _ = np.histogram(data[frame_number], HIST_BINS)
                for count, rect in zip(n, bar_container.patches):
                    rect.set_height(count)
                return_objects = bar_container.patches
                if expectation_line:
                    expectation_line.set_xdata([expectations[frame_number], expectations[frame_number]])
                    return_objects.append(expectation_line)
                if std_line_0 and std_line_1:
                    std_line_0.set_xdata([stds[frame_number][0], stds[frame_number][0]])
                    std_line_1.set_xdata([stds[frame_number][1], stds[frame_number][1]])
                    return_objects.append(std_line_0)
                    return_objects.append(std_line_1)
                return return_objects

            return animate

        fig, ax = plt.subplots()
        _, _, bar_container = ax.hist(data[0], HIST_BINS, lw=1, ec="yellow", fc="blue", alpha=0.5)
        expectation_line = None
        if expectations:
            expectation_line = ax.axvline(x=expectations[0], color="red", linewidth=2)
            text = "$\mathbb{E}(" + str(goal) + "_n)$" if self.is_probabilistic else f"${goal}_n$"
            labels.append(Line2D([0], [0], label=text, color="red"))
        std_line_0 = None
        std_line_1 = None
        if stds:
            std_line_0 = ax.axvline(x=stds[0][0], linestyle="dotted", color="red", linewidth=2)
            std_line_1 = ax.axvline(x=stds[0][1], linestyle="dotted", color="red", linewidth=2)
            labels.append(Line2D([0], [0], linestyle=":", label="$\pm 2 Std(" + str(goal) + "_n)$", color='red'))
        ax.set_ylim(top=self.max_y if self.max_y else number_samples / 2)
        self.fps = min(int(number_iter / self.anim_time), 30)
        number_rendered_frames = int(self.fps * self.anim_time)
        frames_factor = number_iter / number_rendered_frames
        self.ani = animation.FuncAnimation(fig, func=prepare_animation(bar_container, expectation_line, std_line_0,
                                                                       std_line_1), interval=int(1000 / self.fps),
                                           frames=number_rendered_frames, repeat=False)
        description = f"[{goal.args[1]}]" if isinstance(goal, Piecewise) else str(goal)
        plt.xlabel(f"Empirical distribution of {description}")
        plt.ylabel("Counts")
        if labels:
            ax.legend(handles=labels)
        self.plt = plt

    def save(self, filename):
        self.ani.save(filename + ".gif", fps=self.fps)

    def draw(self):
        plt.show()
