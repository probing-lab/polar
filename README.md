# Polar - Polynomial Invariants for Unbounded Support Distributions

This readme is specifically tailored for the extension to Invariants for Unbounded Support Distributions. Otherwise see `README_tool.md`. The branch can be found under [https://github.com/probing-lab/polar/tree/ost-extension](https://github.com/probing-lab/polar/tree/ost-extension)

It allows for reproduction of **Table 1**.

## Content

- [Polar - Polynomial Invariants for Unbounded Support Distributions](#polar---polynomial-invariants-for-unbounded-support-distributions)
  - [Content](#content)
  - [Installation](#installation)
  - [CLI](#cli)
  - [Reproducing the results](#reproducing-the-results)
    - [Figure 1](#figure-1)
    - [Figure 2](#figure-2)



## Installation

To install Polar locally, you can perform the following steps.

1. Ensure you have python and pip installed.

2. Clone the repository.

3. Recommended: Create a virtual environment in the `.venv` directory (you might need to install [virtualenv](https://docs.python.org/3/library/venv.html) first):
```bash
python -m venv .venv
```

4. Activate the virtual environment:
```bash
source .venv/bin/activate
```

5. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## CLI

```
python polar.py --ost [program]
```
- `-N [N]` assume that $E(T^N)<\infty$
- `-lb [x] [b]` assume that (after termination) it holds that $x_T\geq b$. 
- `-lb [x]0 [b]` assume that $x_0\geq b$. 
- `-ub [x] [b]` assume that (after termination) it holds that $x_T\leq b$. 
- `-ub [x]0 [b]` assume that $x_0\leq b$.
- `-iter_var [k]` the variable that tracks the iteration number (default $k$).
- `--milp_solver [CBC]` the MILP solver to use for the Martingale synthesis (default `CBC`)
- `-o [location]` the location of the csv file in which to save the bounds.

## Reproducing the results
The tool uses aggressive (and thus potentially suboptimal) subsumption checking. Thus the tool in general is nondeterministic, and although results can be reliably reproduced, this can be guaranteed by setting the environment variable `PYTHONHASHSEED=0`.

**Compute time: ~10s**

### Figure 1
Running the following command computes the bound.
```bash
PYTHONHASHSEED=0 python polar.py --ost benchmarks/ost/running_example.prob -N 2 -lb x -1 -o outputs/fig1.csv
```

Verify reproduction (output should be empty):
```bash
diff outputs/fig1.csv outputs/expected/fig1.csv
```

### Figure 2
```bash
PYTHONHASHSEED=0 python polar.py --ost benchmarks/ost/running_example_unbounded.prob -N 3 -lb "E(x)" "(-13/10)" -ub "E(x**2)" "(23/10)" -o outputs/fig2.csv
```

Verify reproduction (output should be empty):
```bash
diff outputs/fig2.csv outputs/expected/fig2.csv
```