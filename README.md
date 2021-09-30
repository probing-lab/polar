[![Build & Tests](https://github.com/probing-lab/polar/actions/workflows/build-and-tests.yml/badge.svg)](https://github.com/probing-lab/polar/actions/workflows/build-and-tests.yml)

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
