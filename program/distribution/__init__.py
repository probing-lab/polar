from .bernoulli import *
from .categorical import *
from .distribution import *
from .normal import *
from .laplace import *
from .exponential import *
from .uniform import *
from .discrete_uniform import *

__distributions__ = {
    "Bernoulli": Bernoulli,
    "Normal": Normal,
    "Categorical": Categorical,
    "Uniform": Uniform,
    "DiscreteUniform": DiscreteUniform,
    "Laplace": Laplace,
    "Exponential": Exponential
}


def distribution_factory(dist_name: str, parameters) -> Distribution:
    if dist_name in __distributions__:
        return __distributions__[dist_name](parameters)
    raise RuntimeError(f"Distribution {dist_name} is not supported")
