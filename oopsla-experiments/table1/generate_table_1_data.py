import os
import shutil

files_goals = [
    ("running-example", "E(z)"),
    ("herman-3", "E(tokens**3)"),
    ("las-vegas-search", "E(found**20)"),
    ("pi-approximation", "E(count**3)"),
    ("50-coin-flips", "E(total)"),
    ("gambler-ruin-momentum", "E(x**3)"),
    ("hawk-dove-symbolic", "E(p1bal**4)"),
    ("variable-swap", "E(x**30)"),
    ("retransmission-protocol", "E(fail**3)"),
    ("randomized-response", "E(p1**3)"),
    ("duelling-cowboys", "E(ahit)"),
    ("martingale-bet", "E(capital**3)"),
    ("bimodal", "E(x**10)"),
    ("dbn-umbrella", "E(umbrella**5)"),
    ("dbn-component-health", "E(obs**5)"),
]


def generate_data():
    print()
    if os.path.exists("outputs"):
        shutil.rmtree("outputs")
    os.mkdir("outputs")
    for file, goal in files_goals:
        print(f"Execute Polar on {file} with goal {goal}")
        command = f'python ../../polar.py ../../benchmarks/oopsla/table1/{file}.prob --goals "{goal}" > outputs/{file}.out'
        os.system(command)
    print()


def generate_summary():
    print("Generate summary")
    summary = ""
    for file_name, _ in files_goals:
        with open(f"outputs/{file_name}.out", "r") as file:
            for line in file:
                if line.startswith("Elapsed time"):
                    summary += f"{file_name}\n{line}\n"
    with open("outputs/summary.out", "w") as sfile:
        sfile.write(summary)


if __name__ == "__main__":
    print("Generating the data for table 1")
    generate_data()
    generate_summary()
    print("Finished. The outputs can be found in the folder 'outputs'.")
