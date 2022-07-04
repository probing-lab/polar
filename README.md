[![Build & Tests](https://github.com/probing-lab/polar/actions/workflows/build-and-tests.yml/badge.svg)](https://github.com/probing-lab/polar/actions/workflows/build-and-tests.yml)

<p align="center">
  <img src="https://github.com/probing-lab/polar/blob/master/logo-dark.svg" width=300/>
</p>


# Polar

## OOPSLA Artifact


To reproduce the results of the OOPSLA paper use the scripts in the folder `oopsla-experiments`.

First, make sure you have a running installation of Polar (for example using the Docker image).
Then, enter the python virtual environment:

```
source .venv/bin/activate
```

For every example, figure and table from the OOPSLA paper relevant to the artifact, there is a sub-folder in the `oopsla-experiments`
folder. Every sub-folder contains a script to reproduce the respective results as well as the expected outputs.

For instance to reproduce Table 1 run:
```
cd oopsla-experiments/table1
python generate_table_1_data.py
```

After the script terminates the produced outputs can be found in `oopsla-experiments/table1/outputs`.
The expected outputs are in `oopsla-experiments/table1/expected-outputs`.

The outputs contain the log files of Polar and for tables an additional `summary` file that collects the relevant
information for the respective table.

The log files of Polar contain the tools output.
Polar computes the exact moments of program variable monomials.
For instance a log file could contain a line like:

````
E(x**3) = 0; 2; 3; n+1
````

This means that the third raw moment of program variable `x` is `0` at iteration 0, `2` at iteration 1,
`3` at iteration 2 and `n+1` for iterations n>2.
In general, moments always start with some initial values true for the first few iterations, followed by a general
expression for the moment which holds after the first few iterations.


## Local Installation


To install Polar, you can do the following steps.

1. Make sure you have python (version &geq; 3.8) and pip installed on your system.
Otherwise install it in your preferred way.

2. Clone the repository:

```
git clone git@github.com:probing-lab/polar.git
cd polar
```

3. Create a virtual environment in the `.venv` directory:
```
pip install --user virtualenv
python -m venv .venv
```

4. Activate the virtual environment:
```
source .venv/bin/activate
```

5. Install the required dependencies:
```
pip install -r requirements.txt
```

## Usage

To compute the exact expected value of program variable `z` on the benchmark `benchmarks/polar_paper/illustrating.prob` you can execute the following line:

```
python polar.py benchmarks/polar_paper/illustrating.prob --goals "E(z)"
```

The parameter `goals` takes any expected value of monomials of program variables, for instance `"E(x**2)"`, `"E(t*x**2)"`, etc.
To compute the variance you can pass `"c2(x)"`.
In general, to compute the kth central moment (where k is a natural number), pass `"ck(x)"` to the goals parameter.

For a list of all parameters supported by Polar run:

```
python polar.py --help
```


## Run Tests

You can run the automatic test suite with:

```
python -m unittest
```

To run `flake8`, a tool for style guide enforcement, first install it with:
```
pip install flake8
```

After installation `flake8` can be executed by running:
```
flake8 .
```
