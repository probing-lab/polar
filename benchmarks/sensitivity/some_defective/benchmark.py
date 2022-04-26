#!/usr/bin/env python3

import os
import subprocess
from dataclasses import dataclass
from typing import List

# can either be "sensitivity_analysis_diff" or "sensitivity_analysis"
# NOTE: these benchmarks are supposed to be run only with the latter option
SENSITIVITY_TYPE = "sensitivity_analysis"

# path to the folder where polar is located
POLAR_DIR = "../../../"

# benchmarks are assumed to be in the same dir as the script
BENCHMARK_FOLDER = os.getcwd()

TIMEOUT_SECS = 120

@dataclass
class Benchmark:
    filename: str
    goals: List[str]
    param: str
    results: List[str] = None
    duration_sec: float = 0.0
    system_size: int = 0
    successful: bool = False

# Add, alter or remove benchmarks here in the format "filename", [goals], "parameter"
benchmarks = [
    Benchmark("diff_effective.prob", ["E(y)"], "par"), 
    Benchmark("diff_effective_2.prob", ["E(u)"], "p"), 
    Benchmark("diff_effective_3.prob", ["E(total)"], "p"), 
    Benchmark("diff_effective_4.prob", ["E(z)"], "p1"),
    Benchmark("../all_effective/bimodal_x.prob", ["E(x)"], "var"),
    Benchmark("../all_effective/bimodal_x.prob", ["E(x**2)"], "var"),
    Benchmark("../all_effective/dbn_component_health.prob", ["E(obs)"], "p1"),
    Benchmark("../all_effective/dbn_component_health.prob", ["E(obs**2)"], "p1"),
    Benchmark("../all_effective/gambling.prob", ["E(money)"], "p"),
    Benchmark("../all_effective/gambling.prob", ["E(money**2)"], "p"),
    Benchmark("../all_effective/las_vegas_search.prob", ["E(attempts)"], "p"),
    Benchmark("../all_effective/las_vegas_search.prob", ["E(attempts**2)"], "p"),
    Benchmark("../all_effective/randomized_response.prob", ["E(p1)"], "p"),
    Benchmark("../all_effective/randomized_response.prob", ["E(p1**2)"], "p"),
    Benchmark("../all_effective/vaccination_succinct.prob", ["E(infected)"], "vax_param"),
    Benchmark("../all_effective/vaccination_succinct.prob", ["E(infected**2)"], "vax_param"),
    ]
    
def run_benchmark(benchmark: Benchmark, output):
    print(f"Running benchmark {benchmark.filename}...")
    str_goals = "\"" + "\" \"".join(benchmark.goals) + "\""
    cmd = f"python3 polar.py {os.path.join(BENCHMARK_FOLDER, benchmark.filename)} --goals {str_goals} --{SENSITIVITY_TYPE} {benchmark.param}"
    try:
        result = subprocess.check_output(cmd, shell=True, timeout=TIMEOUT_SECS).decode() # need to use shell=True so the goals quotation marks dont get escaped
        output.write(cmd)
        output.write(result)
        benchmark.successful = True
    except subprocess.TimeoutExpired:
        output.write(cmd)
        output.write("TIMEOUT")
        return
    
    # parse runtime from polar output
    time_pattern = "Elapsed time:"
    time_start_index = result.find(time_pattern)
    if time_start_index < 0:
        print(f"Running benchmark {benchmark.filename} failed. Offending command is {cmd}")
        exit()
    
    time_end_index = result.find(" s", time_start_index)
    benchmark.duration_sec = float(result[time_start_index + len(time_pattern) : time_end_index].strip())
    
    # parse system size
    size_pattern = "Number of recurrences is"
    size_start_index = result.find(size_pattern)
    if size_start_index < 0:
        print(f"Running benchmark {benchmark.filename} did not yield a system size. Offending command is {cmd}")
    
    size_end_index = result.find("\n", size_start_index)
    benchmark.system_size = int(result[size_start_index + len(size_pattern) : size_end_index].strip())

    # search for goal result
    benchmark.results = []
    for goal in benchmark.goals:
        goal_pattern = "∂" + goal + " = "
        result_start_index = result.find(goal_pattern)
        if result_start_index < 0:
            print(f"Running benchmark {benchmark.filename} goal {goal} failed. Offending command is {cmd}")
            exit()
        
        result_end_index = result.find("\n", result_start_index)
        benchmark.results.append(result[result_start_index + len(goal_pattern) : result_end_index].strip())
        
    
def print_benchmark(benchmark: Benchmark):
    if benchmark.successful is False:
        print(f"Benchmark {benchmark.filename} could not be solved.")
        return 
    
    print(f"Benchmark {benchmark.filename} using {benchmark.system_size} recurrences solved in {benchmark.duration_sec} seconds.")
    for i in range(len(benchmark.goals)):
        print(f"\t∂{benchmark.goals[i]} wrt {benchmark.param}: {benchmark.results[i]}")
    return

def main():
    # execute all the benchmarks
    with open('benchmark_trace.txt', 'w') as output:
        # change into polar directory for system call
        os.chdir(POLAR_DIR)

        for benchmark in benchmarks:
            run_benchmark(benchmark, output)

    for benchmark in benchmarks:
        print_benchmark(benchmark)

if __name__ == "__main__":
    main()
