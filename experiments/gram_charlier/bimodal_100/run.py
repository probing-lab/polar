import json
import numpy as np
import matplotlib.pyplot as plt
from sympy import sympify, Symbol


def read_data(filename):
    with open(filename, "r") as file:
        ds = json.load(file)
    data = ds[:100000]
    print(len(data))
    return data


def read_function(filename):
    with open(filename, "r") as file:
        fun = sympify(file.read())
    return fun


def multi_plot():
    sim_data = read_data("simulation.json")
    gc_fun_6 = read_function(f"gram_charlier_6.txt")
    gc_fun_12 = read_function(f"gram_charlier_12.txt")
    xs = np.linspace(-90, 60, 100)
    gc_fun_data_6 = [max(0, float(gc_fun_6.subs({Symbol("x"): x}))) for x in xs]
    gc_fun_data_12 = [max(0, float(gc_fun_12.subs({Symbol("x"): x}))) for x in xs]
    fig = plt.figure(figsize=(6, 3))
    ax = fig.add_subplot()
    ax.hist(sim_data, density=True, bins=5000, color="darkgrey", label="Samples")
    ax.plot(xs, gc_fun_data_12, color="darkblue", linewidth=2, label="GC Order 12")
    ax.plot(
        xs,
        gc_fun_data_6,
        color="red",
        linewidth=2,
        linestyle="dashdot",
        label="GC Order 6",
    )
    ax.yaxis.set_major_formatter(plt.FormatStrFormatter("%.2f"))
    ax.legend(loc="upper right")
    # plt.show()
    plt.savefig("gc_plot_100.pdf")


if __name__ == "__main__":
    multi_plot()
