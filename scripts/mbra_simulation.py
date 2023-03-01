import numpy as np
import scipy.stats as stats


num_samples = 10**6


def f(j):
    if (j+1) % 1000 == 0:
        print(j+1)
    theta1 = stats.uniform.rvs(loc=-0.1, scale=0.2)
    theta2 = stats.norm.rvs(loc=np.pi/4, scale=1)
    theta3 = stats.gamma.rvs(1, scale=2)
    return stats.uniform.rvs(loc=-0.1, scale=0.2) + np.cos(theta1) * (0.5 * np.cos(theta2 + theta3) + np.cos(theta2))


samples = np.arange(num_samples)
samples = np.vectorize(f)(samples)
print(np.average(samples))
