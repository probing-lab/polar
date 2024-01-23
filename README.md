[![Build & Tests](https://github.com/probing-lab/polar/actions/workflows/build-and-tests.yml/badge.svg)](https://github.com/probing-lab/polar/actions/workflows/build-and-tests.yml)

<p align="center">
  <img src="https://github.com/probing-lab/polar/blob/master/logo-dark.svg" width=200/>
</p>


# Polar - A Probabilistic Loop Analyzer

## Content

- [Introduction](#introduction)
- [Installation](#installation)
- [Supported loops](#supported-loops)
- [Usage](#usage)
- [Run tests](#run-tests)
- [For development](#for-development)
- [Cite Polar](#cite-polar)

## Introduction

Polar is a static analyzer for probabilistic while-loops. Classical loops without probabilities are special cases
of probabilistic loops. Therefore, Polar can analyze classical loops as well. Its central functionality is
the computation of closed-form formulas for variables within a loop.
Consider this simple example:

```python
a,b = 0, 1
while true:
    a, b = b, a + b
end
```

This non-probabilistic loop calculates all Fibonacci numbers indefinitely. Although it never terminates,
Polar can still analyze it. For variable `a`, Polar computes the following formula:

```python
a = 0, 1, -sqrt(5)*(1/2 - sqrt(5)/2)**n/5 + sqrt(5)*(1/2 + sqrt(5)/2)**n/5
```

This means a starts at `0`, then `1`, with all subsequent values succinctly represented in the formula.
This formula provides the `n`th Fibonacci number for any number of loop iterations `n`.

Beyond computing formulas for loop variables, Polar offers additional functionalities.
For example, it can compute invariants for loops, which are relationships between loop variables that
remain true before and after every iteration. For the Fibonacci example, Polar provides the following invariant:

```python
a**4 + 2*a**3*b - a**2*b**2 - 2*a*b**3 + b**4 - 1 = 0
```

Polar also handles probabilistic loops. Here's another example:

```python
x,y = 0, 0
while true:
    x = x + 1 {1/2} x - 1
    y = y + 1 {1/2} y - 1
end
```

This loop represents two symmetric random walks. Both `x` and `y` start at `0` and are independently incremented or
decremented by `1` with a probability of `1/2`. Polar provides formulas for moments such as the expected values
of these variables:

```python
E(x) = 0
E(y) = 0
```

Both expected values remain `0`.
However, Polar can also calculate higher moments, like variances, which vary in this example:

```python
c2(x) = n
c2(y) = n
```

The variances (second central moments) of both `x` and `y` follow the formula `n`.
Therefore, the number of loop iterations `n` affects the variances of these variables.
Polar computes invariants for this probabilistic loop as well,
focusing on moments of program variables rather than their values.
For example, it computes the following invariants for the expected values and variances of `x` and `y`:

```python
E(y) = 0
c2(x) - c2(y) = 0
E(x) = 0
```

Based on the functionality to compute closed-form formulas for moments of loop variables, Polar provides many
more functionalities to statically analyze such loops.
You can use Polar through its CLI interface or integrate it into your Python files ([see usage](#usage)).

## Installation

To install Polar locally, you can perform the following steps.

1. Ensure you have python (version &geq; 3.8) and pip installed. If not, install them as preferred.

2. Clone the repository:

```bash
git clone git@github.com:probing-lab/polar.git
cd polar
```

3. Create a virtual environment in the `.venv` directory:
```bash
pip install --user virtualenv
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

## Supported Loops

The problems Polar can solve are uncomputable for arbitrary probabilistic loops. This means that an algorithm and a
tool capable of handling any loop do not exist. Consequently, Polar imposes certain restrictions on the loops it can
analyze. However, if an input loop meets these restrictions, Polar is guaranteed to be able to analyze it, although
the process can be time-consuming. In many cases, though, Polar is quite efficient. The loops for Polar are written in a
custom language. Here's an example:

```python
x,y = 1,0
while true:
    c1 = Bernoulli(1/2)
    c2 = Bernoulli(1/2)
    if c1 + c2 < 2:
        y = y + 1 {1/2} y - 2 {1/3} y
        g = Normal(y,1)
        x = x + g**2
    end
end
```

Generally, the input loops for Polar consist of a section for initial variable assignments followed by a while loop.
Standard arithmetic is allowed in variable assignments, using Python syntax.
Additionally, you can draw from common probability distributions such as `Bernoulli` and `Normal`.
Polar also supports expressions for probabilistic choice. For instance, `y` is assigned `y+1` with probability `1/2`,
`y-2` with probability `1/3`, and to `y` otherwise. The use of `if` statements, `if-elif-else` statements,
and loop guards are also possible.


### Loop Restrictions

For Polar to analyze input loops, they must adhere to the following restrictions:

1. **All variables in if-conditions and the loop guard must only assume finitely many values.**
2. **All probabilities and distribution parameters must be constant**
3. **Non-linear variable dependencies must be acylcic.**

Ad restriction 1:
In the example, both `c1` and `c2` are drawn from Bernoulli distributions and hence are only `0` or `1`.
It is acceptable to use them in conditions and guards. However, `y` cannot be used in conditions and guards, as
it could potentially assume any natural number.

Ad restriction 2:
For some distributions, such as `Normal`, it is permissible to use non-constant distribution parameters.

Ad restriction 3:
The restriction forbids variables `v1`, ... `vk`, where `v1` depends on `v2`, `v2` on `v3`, ...,
`vk` depends on `v1`, with at least one of these dependencies being non-linear.
In the example `x` depends non-linearly on `g` (through `g**2` in the assignment of `x`).
However, since `g` does not depend on `x` this non-linear dependency is acceptable.

There is technically one more restriction: programs can only draw from distributions for which all moments exist.
However, the syntax for the input loops only allows such distributions.

If your input program satisfies these restrictions, Polar theoretically guarantees its analyzability.
Dropping any these restrictions leads to uncomputability or serious hardness barriers.
For more details on the hardness barriers see your publication [Strong Invariants Are Hard](https://arxiv.org/abs/2307.10902).

For more details on the syntax of input programs and Polar itself see your
publication [This Is the Moment for Probabilistic Loops](https://arxiv.org/abs/2204.07185).


## Usage

### Computing Closed-Form Formulas

Polar's core functionality lies in computing closed-form formulas for variables within a (probabilistic) loop.
These formulas, parameterized by the number of loop iterations `n`, provide the value of a given program variable after `n` iterations.
In probabilistic loops, instead of direct values, the formulas describe the moments of program variables.
For example, to compute the expected value of the variable `x` in a probabilistic loop located in `documentation/loops/loop.prob`,
execute the following command:

```bash
python polar.py documentation/loops/loop.prob --goals "E(x)"
```

In this case, Polar provides the following closed-form formula for the expected value of `x`:

```
E(x) = 1; n**3/256 + 133*n**2/256 + 205*n/128 + 1
```

This means that the expected value of `x` is initially `1` and subsequent values are succinctly represented
by the formula parameterized by the number of loop iterations `n`.

The parameter `goals` accepts expected value of monomials of program variables, for instance `"E(x**2)"`, `"E(t*x**2)"`, and so on.
To compute the variance use `"c2(x)"`.
For the kth central moment (where k is a natural number), use `"ck(x)"`.

### Computing Invariants

To compute polynomial invariants among the expected values and variances of `x` and `y`, include all these moments
in the `goal` parameter and additionally pass the `invariant` parameter:

```bash
python polar.py documentation/loops/loop.prob --goals "E(x)" "E(y)" "c2(x)" "c2(y)" --invariants
```

Polar will then output formulas for all the moments specified in the `goals` parameter, along with the following three invariants:

```python
E(x) - 1024*c2(y)**3/658503 - 2128*c2(y)**2/7569 - 205*c2(y)/174 - 1 = 0
E(y) + 8*c2(y)/87 = 0
c2(x) - 6864896*c2(y)**5/4984209207 - 22626304*c2(y)**4/171869283 - 1252660*c2(y)**3/1975509 - 291097*c2(y)**2/181656 - 131467*c2(y)/33408 = 0
```

These are not just any invariants; they form a basis for all polynomial invariants among the moments specified in `goals`.
For more details on why these constitute a basis, refer to moment invariant ideals in the paper [Strong Invariants Are Hard](https://arxiv.org/abs/2307.10902).

To compute invariants for non-probabilistic loops, such as the loop that calculates Fibonacci numbers, omit the `goals` parameter:

```bash
python polar.py documentation/loops/fibonacci.prob --invariants
```

In this case, Polar provides the following invariant:

```python
a**4 + 2*a**3*b - a**2*b**2 - 2*a*b**3 + b**4 - 1 = 0
```

This invariant is a basis for *all* polynomial invariants among the program variables `a` and `b`. As `a` and `b`
represent two consecutive Fibonacci numbers in this example, the invariant encapsulates all polynomial identities
that hold between two consecutive Fibonacci numbers.

For a list of all parameters supported by Polar run:

```
python polar.py --help
```


## Run Tests

You can run the automatic test suite with:

```bash
python -m unittest
```


## For Development

When contributing to Polar, please run the following command after cloning the repository:

```bash
pre-commit install
```

The command installs a few hooks that execute before every commit and enforces some code style guides.


## Cite Polar

If you are writing a scientific paper and want to cite Polar, please cite the following publication:
```
@article{DBLP:journals/pacmpl/MoosbruggerSBK22,
  author       = {Marcel Moosbrugger and
                  Miroslav Stankovic and
                  Ezio Bartocci and
                  Laura Kov{\'{a}}cs},
  title        = {This is the moment for probabilistic loops},
  journal      = {Proc. {ACM} Program. Lang.},
  volume       = {6},
  number       = {{OOPSLA2}},
  pages        = {1497--1525},
  year         = {2022},
  url          = {https://doi.org/10.1145/3563341},
  doi          = {10.1145/3563341},
  timestamp    = {Mon, 05 Dec 2022 13:35:13 +0100},
  biburl       = {https://dblp.org/rec/journals/pacmpl/MoosbruggerSBK22.bib},
  bibsource    = {dblp computer science bibliography, https://dblp.org}
}
```
