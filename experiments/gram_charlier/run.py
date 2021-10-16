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


def plot_for_order(order, sim_data):
    gc_fun = read_function(f"gram_charlier_{order}.txt")
    xs = np.linspace(-20, 20, 100)
    gc_fun_data = [float(gc_fun.subs({Symbol("x"): x})) for x in xs]
    plt.hist(sim_data, density=True, bins=100, color="cornflowerblue")
    plt.plot(xs, gc_fun_data, color="red", linewidth=2)
    plt.title(f"Gram-Charlier {order}")
    plt.show()


def main():
    sim_data = read_data("simulation.json")
    for order in range(4, 21, 2):
        plot_for_order(order, sim_data)


def multi_plot():
    sim_data = read_data("simulation.json")
    gc_fun_8 = read_function(f"gram_charlier_8.txt")
    gc_fun_18 = read_function(f"gram_charlier_18.txt")
    xs = np.linspace(-20, 20, 100)
    gc_fun_data_8 = [float(gc_fun_8.subs({Symbol("x"): x})) for x in xs]
    gc_fun_data_18 = [float(gc_fun_18.subs({Symbol("x"): x})) for x in xs]
    fig, ax = plt.subplots()
    ax.hist(sim_data, density=True, bins=100, color="darkgrey", label="Samples")
    ax.plot(xs, gc_fun_data_18, color="darkblue", linewidth=2, label="GC Order 8")
    ax.plot(xs, gc_fun_data_8, color="deeppink", linewidth=2, linestyle="dashdot", label="GC Order 18")
    ax.yaxis.set_major_formatter(plt.FormatStrFormatter('%.2f'))
    ax.legend()
    plt.savefig("gc_plot.pdf")


if __name__ == "__main__":
    multi_plot()
