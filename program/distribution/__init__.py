from .bernoulli import Bernoulli
from .categorical import Categorical
from .distribution import Distribution
from .normal import Normal
from .laplace import Laplace
from .exponential import Exponential
from .truncated_normal import TruncNormal
from .uniform import Uniform
from .discrete_uniform import DiscreteUniform
from .beta import Beta
from .gamma import Gamma

_distributions = {
    "Bernoulli": Bernoulli,
    "Normal": Normal,
    "Categorical": Categorical,
    "Uniform": Uniform,
    "DiscreteUniform": DiscreteUniform,
    "Laplace": Laplace,
    "DistExp": Exponential,
    "TruncNormal": TruncNormal,
    "Beta": Beta,
    "Gamma": Gamma,
}


def distribution_factory(dist_name: str, parameters) -> Distribution:
    if dist_name in _distributions:
        return _distributions[dist_name](parameters)
    raise RuntimeError(f"Distribution {dist_name} is not supported")
