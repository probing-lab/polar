import os
import shutil


def generate_data():
    print()
    if os.path.exists("outputs"):
        shutil.rmtree("outputs")
    os.mkdir("outputs")
    print()

    print("Run Polar on running-example")
    os.system('python ../../polar.py ../../benchmarks/oopsla/table3/running-example.prob --goals "E(z)" --at_n 10 > outputs/polar-running-example.out')

    print("Run Polar on retransmission-protocol")
    os.system('python ../../polar.py ../../benchmarks/oopsla/table3/retransmission-protocol.prob --goals "E(fail)" --at_n 10 > outputs/polar-retransmission-protocol.out')

    print("Run Polar on variable-swap")
    os.system('python ../../polar.py ../../benchmarks/oopsla/table3/variable-swap.prob --goals "E(y)" --at_n 10 > outputs/polar-variable-swap.out')

    print("Run Polar on hawk-dove-symbolic")
    os.system('python ../../polar.py ../../benchmarks/oopsla/table3/hawk-dove-symbolic.prob --goals "E(p1bal)" --at_n 10 > outputs/polar-hawk-dove-symbolic.out')

    print("Compute 95-CI (100 samples) for running example")
    os.system('python ../../polar.py ../../benchmarks/oopsla/table3/running-example.prob --goals "E(z)" --simulate --simulation_iter 10 --number_samples 100 > outputs/CI-100-running-example.out')
    print("Compute 95-CI (1000 samples) for running example")
    os.system('python ../../polar.py ../../benchmarks/oopsla/table3/running-example.prob --goals "E(z)" --simulate --simulation_iter 10 --number_samples 1000 > outputs/CI-1000-running-example.out')
    print("Compute 95-CI (100000 samples) for running example")
    os.system('python ../../polar.py ../../benchmarks/oopsla/table3/running-example.prob --goals "E(z)" --simulate --simulation_iter 10 --number_samples 100000 > outputs/CI-100000-running-example.out')

    print("Compute 95-CI (100 samples) for retransmission-protocol")
    os.system('python ../../polar.py ../../benchmarks/oopsla/table3/retransmission-protocol.prob --goals "E(fail)" --simulate --simulation_iter 10 --number_samples 100 > outputs/CI-100-retransmission-protocol.out')
    print("Compute 95-CI (1000 samples) for retransmission-protocol")
    os.system('python ../../polar.py ../../benchmarks/oopsla/table3/retransmission-protocol.prob --goals "E(fail)" --simulate --simulation_iter 10 --number_samples 1000 > outputs/CI-1000-retransmission-protocol.out')
    print("Compute 95-CI (100000 samples) for retransmission-protocol")
    os.system('python ../../polar.py ../../benchmarks/oopsla/table3/retransmission-protocol.prob --goals "E(fail)" --simulate --simulation_iter 10 --number_samples 100000 > outputs/CI-100000-retransmission-protocol.out')

    print("Compute 95-CI (100 samples) for variable-swap")
    os.system('python ../../polar.py ../../benchmarks/oopsla/table3/variable-swap.prob --goals "E(y)" --simulate --simulation_iter 10 --number_samples 100 > outputs/CI-100-variable-swap.out')
    print("Compute 95-CI (1000 samples) for variable-swap")
    os.system('python ../../polar.py ../../benchmarks/oopsla/table3/variable-swap.prob --goals "E(y)" --simulate --simulation_iter 10 --number_samples 1000 > outputs/CI-1000-variable-swap.out')
    print("Compute 95-CI (100000 samples) for variable-swap")
    os.system('python ../../polar.py ../../benchmarks/oopsla/table3/variable-swap.prob --goals "E(y)" --simulate --simulation_iter 10 --number_samples 100000 > outputs/CI-100000-variable-swap.out')

    print("Compute 95-CI (100 samples) for hawk-dove-symbolic")
    os.system('python ../../polar.py ../../benchmarks/oopsla/table3/hawk-dove-symbolic.prob --goals "E(p1bal)" --simulate --simulation_iter 10 --number_samples 100 > outputs/CI-100-hawk-dove-symbolic.out')
    print("Compute 95-CI (1000 samples) for hawk-dove-symbolic")
    os.system('python ../../polar.py ../../benchmarks/oopsla/table3/hawk-dove-symbolic.prob --goals "E(p1bal)" --simulate --simulation_iter 10 --number_samples 1000 > outputs/CI-1000-hawk-dove-symbolic.out')
    print("Compute 95-CI (100000 samples) for hawk-dove-symbolic")
    os.system('python ../../polar.py ../../benchmarks/oopsla/table3/hawk-dove-symbolic.prob --goals "E(p1bal)" --simulate --simulation_iter 10 --number_samples 100000 > outputs/CI-100000-hawk-dove-symbolic.out')
    print()


def generate_summary():
    print("Generating summary")
    summary = ""
    summary += get_summary_for_file("running-example")
    summary += get_summary_for_file("retransmission-protocol")
    summary += get_summary_for_file("variable-swap")
    summary += get_summary_for_file("hawk-dove-symbolic")
    with open("outputs/summary.out", "w") as sfile:
        sfile.write(summary)


def get_summary_for_file(file_name):
    summary = f"{file_name}\n"

    out_file = f"outputs/CI-100-{file_name}.out"
    summary += f"100 Samples - {__get_line_starting_with__(out_file, '95-CI')}"
    out_file = f"outputs/CI-1000-{file_name}.out"
    summary += f"1000 Samples - {__get_line_starting_with__(out_file, '95-CI')}"
    out_file = f"outputs/CI-100000-{file_name}.out"
    summary += f"100000 Samples - {__get_line_starting_with__(out_file, '95-CI')}"
    out_file = f"outputs/CI-100000-{file_name}.out"
    summary += f"CI 1000000 samples - {__get_line_starting_with__(out_file, 'Elapsed time')}"

    out_file = f"outputs/polar-{file_name}.out"
    summary += f"Polar - {__get_line_starting_with__(out_file, 'Elapsed time')}"
    summary += "\n"
    return summary


def __get_line_starting_with__(file_path, staring_with):
    with open(file_path, "r") as file:
        for line in file:
            if line.startswith(staring_with):
                return line


if __name__ == "__main__":
    print("Generating the data for table 3")
    generate_data()
    generate_summary()
    print("Finished. The outputs can be found in the folder 'outputs'.")
