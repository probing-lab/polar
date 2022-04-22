#!/usr/bin/env python3

import os
import subprocess
from dataclasses import dataclass
from typing import List

# can either be "sensitivity_analysis_diff" or "sensitivity_analysis"
SENSITIVITY_TYPE = "sensitivity_analysis_diff"

# path to the folder where polar is located
POLAR_DIR = "../../../"

# benchmarks are assumed to be in the same dir as the script
BENCHMARK_FOLDER = os.getcwd()

@dataclass
class Benchmark:
    filename: str
    goals: List[str]
    param: str
    results: List[str] = None
    duration_sec: float = 0.0
    
benchmarks = [
    Benchmark("50coinflips.prob", ["E(total)"], "p"), 
    Benchmark("bimodal_x.prob", ["E(x)"], "p"), 
    Benchmark("bimodal_x.prob", ["E(x)"], "var"), 
    Benchmark("dbn_component_health.prob", ["E(obs)"], "p"),
    Benchmark("dbn_umbrella.prob", ["E(rain)"], "u1"),
    # NOT_WORKING Benchmark("geometric.prob", ["E(x)"], "p"), 
    Benchmark("gambling.prob", ["E(money)"], "p"), 
    Benchmark("hawk_dove.prob", ["E(p1bal)"], "v"),
    # NOT_WORKING Benchmark("hermann3.prob", ["E(numtokens)"], "p"),
    # NOT_WORKING Benchmark("hermann5.prob", ["E(numtokens)"], "p"),
    # NOT_WORKING Benchmark("hermann7.prob", ["E(numtokens)"], "p"),
    # NOT_WORKING Benchmark("illustrating.prob", ["E(sum)"], "p_z"),
    Benchmark("las_vegas_search.prob", ["E(attempts)"], "p"),
    Benchmark("random_walk_1d.prob", ["E(x)"], "p"),
    Benchmark("random_walk_2d.prob", ["E(x)", "E(y)"], "p_right"),
    Benchmark("randomized_response.prob", ["E(p1)"], "p"),
    Benchmark("rock_paper_scissors.prob", ["E(p1bal)"], "p1"),
    ]
    
def run_benchmark(benchmark: Benchmark, output):
    print(f"Running benchmark {benchmark.filename}...")
    str_goals = "\"" + "\" \"".join(benchmark.goals) + "\""
    cmd = f"python3 polar.py {os.path.join(BENCHMARK_FOLDER, benchmark.filename)} --goals {str_goals} --{SENSITIVITY_TYPE} {benchmark.param}"
    result = subprocess.check_output(cmd, shell=True).decode() # need to use shell=True so the goals quotation marks dont get escaped
    output.write(cmd)
    output.write(result)
    
    # parse runtime from polar output
    time_pattern = "Elapsed time:"
    time_start_index = result.find(time_pattern)
    if time_start_index < 0:
        print(f"Running benchmark {benchmark.filename} failed. Offending command is {cmd}")
        exit()
    
    time_end_index = result.find(" s", time_start_index)
    benchmark.duration_sec = float(result[time_start_index + len(time_pattern) : time_end_index].strip())
    
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
    print(f"Benchmark {benchmark.filename} computed in {benchmark.duration_sec} seconds.")
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
