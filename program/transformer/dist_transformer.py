from functools import singledispatchmethod

from program.assignment import DistAssignment, PolyAssignment
from program.distribution import Normal, Uniform
from program.transformer.transformer import TreeTransformer
from utils import get_unique_var


class DistTransformer(TreeTransformer):
    """
    Exploits the linearity of the normal and uniform distribution to "pull out"
    program variables from the parameters. It does so by introducing a new assignment.
    """

    @singledispatchmethod
    def transform(self, element):
        return element

    @transform.register
    def _(self, dist_assign: DistAssignment):
        if isinstance(dist_assign.distribution, Normal):
            return self.__transform_normal__(dist_assign)

        if isinstance(dist_assign.distribution, Uniform):
            return self.__transform_uniform__(dist_assign)

        return dist_assign

    def __transform_normal__(self, normal_assign):
        variable = normal_assign.variable
        normal: Normal = normal_assign.distribution

        if not normal.mu.free_symbols:
            return normal_assign

        new_var = get_unique_var()
        new_normal_assign = DistAssignment(new_var, Normal([0, normal.sigma2]))
        new_assign = PolyAssignment(variable, f"{normal.mu} + {new_var}")
        return new_normal_assign, new_assign

    def __transform_uniform__(self, uniform_assign):
        variable = uniform_assign.variable
        uniform: Uniform = uniform_assign.distribution

        if not uniform.a.free_symbols and not uniform.b.free_symbols:
            return uniform_assign

        new_var = get_unique_var()
        a, b = str(uniform.a), str(uniform.b)
        new_uniform_assign = DistAssignment(new_var, Uniform([0, 1]))
        new_assign = PolyAssignment(variable, f"{a} + ({b} - ({a}))*{new_var}")
        return new_uniform_assign, new_assign
