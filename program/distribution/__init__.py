from .bernoulli import *
from .categorical import *
from .distribution import *
from .normal import *
from .uniform import *

__distributions__ = {
    "Bernoulli": Bernoulli,
    "Normal": Normal,
    "Categorical": Categorical,
    "Uniform": Uniform,
}


def distribution_factory(dist_name: str, parameters) -> Distribution:
    if dist_name in __distributions__:
        return __distributions__[dist_name](parameters)
    raise RuntimeError(f"Distribution {dist_name} is not supported")
