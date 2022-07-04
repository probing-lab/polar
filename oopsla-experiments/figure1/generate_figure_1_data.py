import os
import shutil

if __name__ == "__main__":
    print("Generating the data for figure 1")
    print()
    if os.path.exists("outputs"):
        shutil.rmtree("outputs")
    os.mkdir("outputs")

    print("Compute E(toggle)")
    os.system('python ../../polar.py ../../benchmarks/oopsla/table1/running-example.prob --goals "E(toggle)" > outputs/toggle.out')
    print("Compute E(x)")
    os.system('python ../../polar.py ../../benchmarks/oopsla/table1/running-example.prob --goals "E(x)" > outputs/x.out')
    print("Compute E(x**2)")
    os.system('python ../../polar.py ../../benchmarks/oopsla/table1/running-example.prob --goals "E(x**2)" > outputs/x2.out')
    print("Compute E(l)")
    os.system('python ../../polar.py ../../benchmarks/oopsla/table1/running-example.prob --goals "E(l)" > outputs/l.out')

    print()
    print("Finished. The outputs can be found in the folder 'outputs'.")
