import os
import shutil

if __name__ == "__main__":
    print("Generating the data for example 6")
    print()
    if os.path.exists("outputs"):
        shutil.rmtree("outputs")
    os.mkdir("outputs")

    print("Compute E(x) after loop")
    os.system('python ../../polar.py ../../benchmarks/polar_paper/geometric.prob --goals "E(x)" --after_loop > outputs/x-after-loop.out')

    print()
    print("Finished. The outputs can be found in the folder 'outputs'.")
