import os
import shutil

if __name__ == "__main__":
    print("Generating the plots for figure 6")
    print()
    if os.path.exists("outputs"):
        shutil.rmtree("outputs")
    os.mkdir("outputs")

    print("Generate plot for running-example")
    os.system('python ../../polar.py ../../benchmarks/oopsla/figure6/running-example.prob --plot z --plot_expectation --plot_std --yscale symlog --simulation_iter 30 --number_samples 200 --save > /dev/null')
    os.system("mv plot.pdf outputs/running-example.pdf")

    print("Generate plot for variable-swap")
    os.system('python ../../polar.py ../../benchmarks/oopsla/figure6/variable-swap.prob --plot y --plot_expectation --plot_std --simulation_iter 30 --number_samples 200 --save > /dev/null')
    os.system("mv plot.pdf outputs/variable-swap.pdf")

    print("Generate plot for hawk-dove-symbolic")
    os.system('python ../../polar.py ../../benchmarks/oopsla/figure6/hawk-dove-symbolic.prob --plot p1bal --plot_expectation --plot_std --simulation_iter 30 --number_samples 200 --save > /dev/null')
    os.system("mv plot.pdf outputs/hawk-dove-symbolic.pdf")

    print()
    print("Finished. The outputs can be found in the folder 'outputs'.")
