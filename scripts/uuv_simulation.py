import numpy as np
import scipy.stats as stats


num_samples = 10**6
n = 10


def f(j):
    if (j + 1) % 1000 == 0:
        print(j + 1)
    x = stats.uniform.rvs(loc=-0.1, scale=0.2)
    y = stats.uniform.rvs(loc=-0.1, scale=0.2)
    theta = stats.uniform.rvs(loc=np.pi / 4 - 0.1, scale=0.2)
    ovs = stats.uniform.rvs(loc=-0.1, scale=0.2, size=n)
    ots = stats.uniform.rvs(loc=-0.1, scale=0.2, size=n)
    for i in range(n):
        x = x + 0.1 * (2 + ovs[i]) * np.cos(theta)
        y = y + 0.1 * (2 + ovs[i]) * np.sin(theta)
        theta = theta + 0.1 * ots[i]
    return x


samples = np.arange(num_samples)
samples = np.vectorize(f)(samples)
samples = samples**2
print(np.average(samples))
