from .bernoulli import Bernoulli
from .categorical import Categorical
from .distribution import Distribution
from .normal import Normal
from .laplace import Laplace
from .exponential import Exponential
from .uniform import Uniform

__distributions__ = {
    "Bernoulli": Bernoulli,
    "Normal": Normal,
    "Categorical": Categorical,
    "Uniform": Uniform,
    "Laplace": Laplace,
    "Exponential": Exponential
}


def distribution_factory(dist_name: str, parameters) -> Distribution:
    if dist_name in __distributions__:
        return __distributions__[dist_name](parameters)
    raise RuntimeError(f"Distribution {dist_name} is not supported")
