import numpy as np
import scipy.stats as stats


num_samples = 10**6
n = 25


def f(j):
    if (j+1) % 1000 == 0:
        print(j+1)
    x = stats.uniform.rvs(loc=-0.1, scale=0.2)
    y = stats.uniform.rvs(loc=-0.1, scale=0.2)
    theta = stats.norm.rvs(loc=0, scale=np.sqrt(0.1))
    ors = stats.beta.rvs(1, 3, size=n)
    ols = stats.uniform.rvs(loc=-0.1, scale=0.2, size=n)
    for i in range(n):
        x = x + 0.05 * (4 + ols[i] + ors[i]) * np.cos(theta)
        y = y + 0.05 * (4 + ols[i] + ors[i]) * np.sin(theta)
        theta = theta + 0.1 * (2 + ors[i] - ols[i])
    return x**2


samples = np.arange(num_samples)
samples = np.vectorize(f)(samples)
print(np.average(samples))
