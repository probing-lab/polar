import os
import shutil

if __name__ == "__main__":
    print("Generating the data for example 5")
    print()
    if os.path.exists("outputs"):
        shutil.rmtree("outputs")
    os.mkdir("outputs")

    print("Compute E(z)")
    os.system('python ../../polar.py ../../benchmarks/oopsla/table1/running-example.prob --goals "E(z)" > outputs/z.out')

    print()
    print("Finished. The outputs can be found in the folder 'outputs'.")
