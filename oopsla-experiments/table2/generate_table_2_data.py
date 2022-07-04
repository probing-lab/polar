import os
import shutil

files_vars = [
    ("coupon", "c"),
    ("coupon4", "c"),
    ("random-walk-1d", "x"),
    ("sum-rnd-series", "x"),
    ("product-dep-var", "p"),
    ("random-walk-2d", "x"),
    ("binomial", "x"),
    ("stuttering-a", "s"),
    ("stuttering-b", "s"),
    ("stuttering-c", "s"),
    ("stuttering-d", "s"),
    ("stuttering-p", "s"),
    ("square", "y"),
]


def generate_data():
    print()
    if os.path.exists("outputs"):
        shutil.rmtree("outputs")
    os.mkdir("outputs")
    for file, variable in files_vars:
        for power in [1, 2, 3]:
            print(f"Execute Polar on {file} with goal E({variable}**{power})")
            command = f'python ../../polar.py ../../benchmarks/oopsla/table2/{file}.prob --goals "E({variable}**{power})" > outputs/{file}-{power}.out'
            os.system(command)
        command_only_parsing = f'python ../../polar.py ../../benchmarks/oopsla/table2/{file}.prob > outputs/{file}-only-parsing.out'
        os.system(command_only_parsing)
    print()


def generate_summary():
    print("Generate summary")
    summary = ""
    for file_name, var in files_vars:
        summary += f"{file_name}\n"
        out_file = f"outputs/{file_name}-1.out"
        summary += f"E({var}) {__get_elapsed_time__(out_file)}"
        out_file = f"outputs/{file_name}-2.out"
        summary += f"E({var}**2) {__get_elapsed_time__(out_file)}"
        out_file = f"outputs/{file_name}-3.out"
        summary += f"E({var}**3) {__get_elapsed_time__(out_file)}"
        out_file = f"outputs/{file_name}-only-parsing.out"
        summary += f"Parsing & transforming {__get_elapsed_time__(out_file)}"
        summary += "\n"
    with open("outputs/summary.out", "w") as sfile:
        sfile.write(summary)


def __get_elapsed_time__(file_path):
    with open(file_path, "r") as file:
        for line in file:
            if line.startswith("Elapsed time"):
                return line


if __name__ == "__main__":
    print("Generating the data for table 2")
    generate_data()
    generate_summary()
    print("Finished. The outputs can be found in the folder 'outputs'.")