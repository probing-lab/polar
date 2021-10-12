from random import random


def run():
    stop = False
    count = 0
    while not stop:
        stop = random() < 0.5
        count += 1
    print(count)


if __name__ == "__main__":
    for _ in range(100):
        run()
