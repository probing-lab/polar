import numpy as np
import scipy.stats as stats


num_samples = 10**6
n = 10


def f(j):
    if (j + 1) % 1000 == 0:
        print(j + 1)
    vx = stats.uniform.rvs(loc=-0.1, scale=0.2)
    vy = stats.uniform.rvs(loc=-0.1, scale=0.2)
    vt = stats.uniform.rvs(loc=-0.1, scale=0.2)
    x = stats.uniform.rvs(loc=-0.1, scale=0.2)
    y = stats.uniform.rvs(loc=0.4, scale=0.1)
    t = stats.uniform.rvs(loc=-0.1, scale=0.2)
    c = 0.065274151
    omegas = stats.uniform.rvs(loc=-0.1, scale=0.2, size=n)
    for i in range(n):
        x = x + 0.1 * vx
        y = y + 0.1 * vy
        vx = vx - 1.202 * np.sin(t)
        vy = vy - 0.98 + 1.202 * np.cos(t)
        t = t + 0.1 * (vt + omegas[i])
        vt = vt + c
    return y


samples = np.arange(num_samples)
samples = np.vectorize(f)(samples)
print(np.average(samples))
