import os
import shutil

if __name__ == "__main__":
    print("Generating the data for figure 2")
    print()
    if os.path.exists("outputs"):
        shutil.rmtree("outputs")
    os.mkdir("outputs")

    print("Compute E(tokens)")
    os.system('python ../../polar.py ../../benchmarks/oopsla/table1/herman-3.prob --goals "E(tokens)" > outputs/tokens.out')

    print("Compute E(tokens**2)")
    os.system('python ../../polar.py ../../benchmarks/oopsla/table1/herman-3.prob --goals "E(tokens**2)" > outputs/tokens2.out')

    print("Compute E(tokens**3)")
    os.system('python ../../polar.py ../../benchmarks/oopsla/table1/herman-3.prob --goals "E(tokens**3)" > outputs/tokens3.out')

    print()
    print("Finished. The outputs can be found in the folder 'outputs'.")
