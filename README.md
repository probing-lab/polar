[![Build & Tests](https://github.com/probing-lab/polar/actions/workflows/build-and-tests.yml/badge.svg)](https://github.com/probing-lab/polar/actions/workflows/build-and-tests.yml)

<p align="center">
  <img src="https://github.com/probing-lab/polar/blob/master/logo-dark.svg" width=300/>
</p>


# Polar

## Installation


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


## For Development

When contributing to Polar, please run the following command after cloning the repository:

```
pre-commit install
```

The command installs a few hooks that execute before every commit and enforces some code style guides.
