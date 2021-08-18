import numpy as np
from symengine.lib.symengine_wrapper import sympify
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.lines import Line2D

from .plot import Plot
from simulation import SimulationResult
from utils import eval_re


class RunsPlot(Plot):

    def __init__(self, simulation_result: SimulationResult, goal, yscale="linear", anim_iter=False, anim_runs=False, anim_time=10, first_moment=None, second_moment=None):
        self.simulation_result = simulation_result
        self.goal = goal
        self.yscale = yscale
        self.anim_iter = anim_iter
        self.anim_runs = anim_runs
        self.anim_time = anim_time
        self.fps = -1
        self.first_moment = first_moment
        self.second_moment = second_moment
        self.plt = None
        self.ani = None
        self.__build__()

    def __build__(self):
        fig, ax = plt.subplots()
        goal = sympify(self.goal)
        plt.ylabel("$\mathbb{R}$", rotation=0)
        ax.set_yscale(self.yscale)
        plt.xlabel("n")
        exact_resolution = 4
        iterations = len(self.simulation_result.samples[0])
        samples = self.simulation_result.samples
        first_moment = self.first_moment
        second_moment = self.second_moment
        store = [[] for _ in range(iterations)]
        frame_factor = 1
        labels = []

        run_data = []
        for run in samples:
            data = [state[goal] for state in run]
            for i in range(len(data)):
                store[i].append(data[i])
            run_data.append(data)
        labels.append(Line2D([0], [0], label="Samples", color="grey"))

        xs = np.linspace(0, len(samples[0]), iterations * exact_resolution)
        if first_moment:
            expectation_data = [eval_re({"n": x}, first_moment) for x in xs]
            labels.append(Line2D([0], [0], label="$\mathbb{E}(" + str(goal) + "_n)$", color="red"))

        if first_moment and second_moment:
            variance = second_moment - (first_moment ** 2)
            std = variance ** (1 / 2)
            std_data_1 = [eval_re({"n": x}, first_moment + 2 * std) for x in xs]
            std_data_2 = [eval_re({"n": x}, first_moment - 2 * std) for x in xs]
            labels.append(Line2D([0], [0], linestyle=":", label="$\pm 2 Std(" + str(goal) + "_n)$", color='red'))

        objects = []

        def iter_animation(frame_number):
            frame_number = int(frames_factor * frame_number)
            for o in objects:
                o.remove()
            objects.clear()
            if first_moment:
                ed = expectation_data[:frame_number * exact_resolution]
                objects.extend(ax.plot(xs[:frame_number * exact_resolution], ed, color="red", linewidth=2))
            if first_moment and second_moment:
                sd1 = std_data_1[:frame_number * exact_resolution]
                sd2 = std_data_2[:frame_number * exact_resolution]
                objects.extend(ax.plot(xs[:frame_number * exact_resolution], sd1, ":", color="red", linewidth=1.5))
                objects.extend(ax.plot(xs[:frame_number * exact_resolution], sd2, ":", color="red", linewidth=1.5))
            for r in run_data:
                objects.extend(ax.plot(range(frame_number), r[:frame_number], linewidth=1, color="grey", alpha=0.1))

        def runs_animation(frame_number):
            frame_number = int(frames_factor * frame_number)
            for o in objects:
                o.remove()
            objects.clear()
            run_index, run_iter = divmod(frame_number, iterations)
            for i in range(run_index):
                objects.extend(ax.plot(range(iterations), run_data[i], linewidth=1, color="grey", alpha=0.1))
            objects.extend(ax.plot(range(run_iter), run_data[run_index - 1][:run_iter], linewidth=1, color="blue"))

        legend = ax.legend(handles=labels)
        if self.anim_iter:
            self.fps = min(int(iterations / self.anim_time), 30)
            number_rendered_frames = int(self.fps * self.anim_time)
            frames_factor = iterations / number_rendered_frames
            iter_animation(number_rendered_frames)
            for o in objects:
                o.remove()
            objects.clear()
            self.ani = animation.FuncAnimation(fig, iter_animation, number_rendered_frames,
                                               interval=int(1000 / self.fps))
        elif self.anim_runs:
            if first_moment:
                ax.plot(xs, expectation_data, color="red", linewidth=2)
            if first_moment and second_moment:
                ax.plot(xs, std_data_1, ":", color="red", linewidth=1.5)
                ax.plot(xs, std_data_2, ":", color="red", linewidth=1.5)
            number_real_frames = len(samples) * iterations
            self.fps = min(int(number_real_frames / self.anim_time), 30)
            number_rendered_frames = int(self.fps * self.anim_time)
            frames_factor = number_real_frames / number_rendered_frames
            runs_animation(number_rendered_frames)
            for o in objects:
                o.remove()
            objects.clear()
            self.ani = animation.FuncAnimation(fig, runs_animation, number_rendered_frames,
                                               interval=int(1000 / self.fps))
        else:
            frames_factor = 1
            iter_animation(iterations)
        self.plt = plt

    def save(self, filename):
        if self.anim_iter or self.anim_runs:
            self.ani.save(filename + ".gif", fps=self.fps)
        else:
            self.plt.savefig(filename + ".pdf")

    def draw(self):
        plt.show()
