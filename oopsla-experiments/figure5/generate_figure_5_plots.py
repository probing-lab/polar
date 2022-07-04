import os
import shutil
import numpy as np
import matplotlib.pyplot as plt

from symengine.lib.symengine_wrapper import Symbol as SymSymbol
from sympy import Symbol as Symbol, sympify

import sys
sys.path.append("../..")

from cli import ArgumentParser
from cli.common import parse_program, prepare_program, get_all_cumulants
from expansions import GramCharlierExpansion
from inputparser import Parser
from simulation import Simulator


def get_bimodal_samples():
    parser = Parser()
    program = parser.parse_file("../../benchmarks/oopsla/figure5/bimodal_x.prob")

    simulation_iter = 100
    number_samples = 10000
    x = SymSymbol("x")
    simulator = Simulator(simulation_iter)
    result = simulator.simulate(program, [x], number_samples)
    samples_iter_10 = [run[10][x] for run in result.samples]
    samples_iter_100 = [run[100][x] for run in result.samples]
    return samples_iter_10, samples_iter_100


def get_bimodal_gc_expansions():
    cli_args = ArgumentParser().get_defaults()
    program = parse_program("../../benchmarks/oopsla/figure5/bimodal_x.prob", cli_args.transform_categoricals)
    program = prepare_program(program, cli_args)
    x = SymSymbol("x")
    n = Symbol("n", integer=True)
    cumulants = get_all_cumulants(program, x, 12, cli_args)
    cumulants_at_10 = {k: v.xreplace({n: 10}) for k, v in cumulants.items()}
    cumulants_at_100 = {k: v.xreplace({n: 100}) for k, v in cumulants.items()}

    gc_at_10_order_6 = GramCharlierExpansion({k: v for k, v in cumulants_at_10.items() if k <= 6})()
    gc_at_10_order_12 = GramCharlierExpansion(cumulants_at_10)()

    gc_at_100_order_6 = GramCharlierExpansion({k: v for k, v in cumulants_at_100.items() if k <= 6})()
    gc_at_100_order_12 = GramCharlierExpansion(cumulants_at_100)()

    return (gc_at_10_order_6, gc_at_10_order_12), (gc_at_100_order_6, gc_at_100_order_12)


def generate_plot_iter_10(samples_iter_10, gcs_at_10):
    sim_data = samples_iter_10
    gc_fun_6 = sympify(gcs_at_10[0])
    gc_fun_12 = sympify(gcs_at_10[1])
    xs = np.linspace(-23, 23, 100)
    gc_fun_data_6 = [max(0, float(gc_fun_6.subs({Symbol("x"): x}))) for x in xs]
    gc_fun_data_12 = [max(0, float(gc_fun_12.subs({Symbol("x"): x}))) for x in xs]
    fig = plt.figure(figsize=(6, 3))
    ax = fig.add_subplot()
    ax.set_xlim(-23, 23)
    ax.set_ylim(0, 0.12)
    ax.hist(sim_data, density=True, bins=200, color="darkgrey", label="Samples")
    ax.plot(xs, gc_fun_data_12, color="darkblue", linewidth=2, label="GC Order 12")
    ax.plot(xs, gc_fun_data_6, color="red", linewidth=2, linestyle="dashdot", label="GC Order 6")
    ax.yaxis.set_major_formatter(plt.FormatStrFormatter('%.2f'))
    ax.legend(loc="upper right")
    plt.savefig("outputs/gc_plot_10.pdf")


def generate_plot_iter_100(samples_iter_100, gcs_at_100):
    sim_data = samples_iter_100
    gc_fun_6 = sympify(gcs_at_100[0])
    gc_fun_12 = sympify(gcs_at_100[1])
    xs = np.linspace(-90, 65, 100)
    gc_fun_data_6 = [max(0, float(gc_fun_6.subs({Symbol("x"): x}))) for x in xs]
    gc_fun_data_12 = [max(0, float(gc_fun_12.subs({Symbol("x"): x}))) for x in xs]
    fig = plt.figure(figsize=(6, 3))
    ax = fig.add_subplot()
    ax.set_xlim(-90, 65)
    ax.set_ylim(0, 0.04)
    ax.hist(sim_data, density=True, bins=200, color="darkgrey", label="Samples")
    ax.plot(xs, gc_fun_data_12, color="darkblue", linewidth=2, label="GC Order 12")
    ax.plot(xs, gc_fun_data_6, color="red", linewidth=2, linestyle="dashdot", label="GC Order 6")
    ax.yaxis.set_major_formatter(plt.FormatStrFormatter('%.2f'))
    ax.legend(loc="upper right")
    plt.savefig("outputs/gc_plot_100.pdf")


if __name__ == "__main__":
    print("Generating the plots for figure 5")
    print()
    if os.path.exists("outputs"):
        shutil.rmtree("outputs")
    os.mkdir("outputs")

    print("Sample bimodal benchmark.")
    samples_iter_10, samples_iter_100 = get_bimodal_samples()

    print("Compute bimodal GC expansions")
    gcs_at_10, gcs_at_100 = get_bimodal_gc_expansions()

    print("Generate plot for iteration 10")
    generate_plot_iter_10(samples_iter_10, gcs_at_10)

    print("Generate plot for iteration 100")
    generate_plot_iter_100(samples_iter_100, gcs_at_100)

    print()
    print("Finished. The outputs can be found in the folder 'outputs'.")
