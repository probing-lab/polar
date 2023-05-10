import numpy as np
import scipy.stats as stats


num_samples = 10**6
n = 20


def f(j):
    if (j + 1) % 1000 == 0:
        print(j + 1)
    psi = stats.beta.rvs(3, 3)
    x = stats.uniform.rvs(loc=-0.1, scale=0.2)
    y = stats.uniform.rvs(loc=-0.1, scale=0.2)
    z = stats.uniform.rvs(loc=0.1, scale=0.2)
    theta = stats.beta.rvs(1, 3)
    ovs = stats.beta.rvs(1, 3, size=n)
    ops = stats.uniform.rvs(loc=-0.1, scale=0.2, size=n)
    ots = stats.norm.rvs(loc=0, scale=np.sqrt(0.3), size=n)
    for i in range(n):
        x = x + 0.1 * (1 + ovs[i]) * np.cos(psi) * np.cos(theta)
        y = y + 0.1 * (1 + ovs[i]) * np.sin(psi) * np.cos(theta)
        z = z + 0.1 * (1 + ovs[i]) * np.sin(theta)
        theta = theta + 0.1 * (1 + ots[i])
        psi = psi + 0.1 * (1 + ops[i])
    return x


samples = np.arange(num_samples)
samples = np.vectorize(f)(samples)
print(np.average(samples))
