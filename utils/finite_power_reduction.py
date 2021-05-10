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
    values_vector = Matrix([v ** power for v in values])
    var_vector = Matrix([tmp_var ** p for p in range(len(values))])
    mat = __get_powers_transf_matrix__(values)
    return (values_vector.T * mat * var_vector)[0], tmp_var


@lru_cache(maxsize=None)
def __get_powers_transf_matrix__(values: Tuple):
    values_vector = Matrix([v for v in values])
    mat = zeros(values_vector.size, values_vector.size)
    for i in range(len(values)):
        for j in range(len(values)):
            if i == 0:
                mat[i, j] = One()
            else:
                mat[i, j] = values_vector[j] ** i
    return mat.inv()
