from random import random


def run():
    count = 0
    x = 1
    while x > 0:
        x = x - 1 if random() < 0.5 else x + 1
        count += 1
    print(count)


if __name__ == "__main__":
    for _ in range(1000):
        run()
