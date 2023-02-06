from .bernoulli import Bernoulli
from .categorical import Categorical
from .distribution import Distribution
from .normal import Normal
from .laplace import Laplace
from .exponential import Exponential
from .truncated_normal import TruncNormal
from .uniform import Uniform
from .discrete_uniform import DiscreteUniform
from. beta import Beta

__distributions__ = {
    "Bernoulli": Bernoulli,
    "Normal": Normal,
    "Categorical": Categorical,
    "Uniform": Uniform,
    "DiscreteUniform": DiscreteUniform,
    "Laplace": Laplace,
    "Exponential": Exponential,
    "TruncNormal": TruncNormal,
    "Beta": Beta,
}


def distribution_factory(dist_name: str, parameters) -> Distribution:
    if dist_name in __distributions__:
        return __distributions__[dist_name](parameters)
    raise RuntimeError(f"Distribution {dist_name} is not supported")
