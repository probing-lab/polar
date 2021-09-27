import json
import numpy as np
import matplotlib.pyplot as plt
from sympy import sympify, Symbol


def read_data(filename):
    with open(filename, "r") as file:
        data = json.load(file)
    return data


def read_function(filename):
    with open(filename, "r") as file:
        fun = sympify(file.read())
    return fun


def plot_for_order(order, sim_data):
    gc_fun = read_function(f"gram_charlier_{order}.txt")
    xs = np.linspace(-20, 20, 100)
    gc_fun_data = [float(gc_fun.subs({Symbol("x"): x})) for x in xs]
    plt.hist(sim_data, density=True, bins=1000, color="cornflowerblue")
    plt.plot(xs, gc_fun_data, color="red", linewidth=2)
    plt.title(f"Gram-Charlier {order}")
    plt.show()


def main():
    sim_data = read_data("simulation.json")
    for order in range(4, 21, 2):
        plot_for_order(order, sim_data)


if __name__ == "__main__":
    main()
