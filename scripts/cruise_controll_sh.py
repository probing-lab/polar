import numpy as np


def run_process():
    x1 = 1
    x2 = 1
    x3 = 1
    u = 1
    y1 = x1
    y2 = x2
    y3 = x3
    pc = 0.4
    for i in range(100):
        # store old values
        x1o = x1
        x2o = x2
        x3o = x3

        # state update
        x1 = 1 * x1o + 0.01 * x2o + 0 * x3o + 0.0001 * u
        x2 = -0.0003 * x1o + 0.9997 * x2o + 0.01 * x3o + 0.0001 * u
        x3 = -0.0604 * x1o - 0.0531 * x2o + 0.9974 * x3o + 0.0247 * u

        is_overrun = np.random.choice([True, False], p=[pc, 1 - pc])

        if not is_overrun:
            u = -872.54 * y1 - 131.49 * y2 - 10.097 * y3

        if not is_overrun:
            y1 = x1
            y2 = x2
            y3 = x3
    return x1**2


if __name__ == "__main__":
    data = []
    for _ in range(1000):
        data.append(run_process())
    print(np.average(data))
