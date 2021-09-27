import json
import matplotlib.pyplot as plt


def read_data(filename):
    with open(filename, "r") as file:
        data = json.load(file)
    return data


def main():
    sim_data = read_data("simulation.json")
    cf4_data = read_data("cornish_fisher_4.json")
    cf6_data = read_data("cornish_fisher_6.json")
    cf8_data = read_data("cornish_fisher_8.json")
    cf10_data = read_data("cornish_fisher_10.json")

    plt.title("Simulation")
    plt.hist(sim_data, bins=1000)
    plt.show()

    plt.title("Cornish-Fisher 4")
    plt.hist(cf4_data, bins=1000)
    plt.show()

    plt.title("Cornish-Fisher 6")
    plt.hist(cf6_data, bins=1000)
    plt.show()

    plt.title("Cornish-Fisher 8")
    plt.hist(cf8_data, bins=1000)
    plt.show()

    plt.title("Cornish-Fisher 10")
    plt.hist(cf10_data, bins=1000)
    plt.show()


if __name__ == "__main__":
    main()
