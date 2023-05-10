from functools import lru_cache
from typing import Tuple
from symengine.lib.symengine_wrapper import Expr, Symbol, Matrix, zeros, One


@lru_cache(maxsize=None)
def get_reduced_powers(values: Tuple, power: int) -> Tuple[Expr, Symbol]:
    """
    For a variable v only taking finitely many values v**n can be written as linear
    combinations of powers < |values|. This function computes this linear combination.
    The values ought be passed as a sorted tuple to enable caching of the result.
    """
    tmp_var = Symbol("t")
    values_vector = Matrix([v**power for v in values])
    var_vector = Matrix([tmp_var**p for p in range(len(values))])
    mat = _get_powers_transform_matrix(values)
    return (values_vector.T * mat * var_vector)[0], tmp_var


@lru_cache(maxsize=None)
def _get_powers_transform_matrix(values: Tuple):
    mat = zeros(len(values), len(values))
    for i in range(len(values)):
        for j in range(len(values)):
            if i == 0:
                mat[i, j] = One()
            else:
                mat[i, j] = values[j] ** i
    return mat.inv()
