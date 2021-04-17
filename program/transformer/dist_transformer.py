from singledispatchmethod import singledispatchmethod
from diofant import fraction

from program.assignment import DistAssignment, PolyAssignment
from program.distribution import Normal, Uniform, Laplace, Exponential
from .exceptions import TransformException
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

        if isinstance(dist_assign.distribution, Laplace):
            return self.__transform_laplace__(dist_assign)

        if isinstance(dist_assign.distribution, Exponential):
            return self.__transform_exponential__(dist_assign)

        return dist_assign

    def __transform_normal__(self, normal_assign):
        variable = normal_assign.variable
        normal: Normal = normal_assign.distribution

        if not self.program.variables.intersection(normal.mu.free_symbols):
            return normal_assign

        new_var = get_unique_var()
        new_normal_assign = DistAssignment(new_var, Normal([0, normal.sigma2]))
        new_assign = PolyAssignment(variable, f"{normal.mu} + {new_var}")
        return new_normal_assign, new_assign

    def __transform_laplace__(self, laplace_assign):
        variable = laplace_assign.variable
        laplace: Laplace = laplace_assign.distribution

        if not self.program.variables.intersection(laplace.mu.free_symbols):
            return laplace_assign

        new_var = get_unique_var()
        new_laplace_assign = DistAssignment(new_var, Laplace([0, laplace.b]))
        new_assign = PolyAssignment(variable, f"{laplace.mu} + {new_var}")
        return new_laplace_assign, new_assign

    def __transform_exponential__(self, exp_assign):
        variable = exp_assign.variable
        exp: Exponential = exp_assign.distribution

        if not self.program.variables.intersection(exp.lamb.free_symbols):
            return exp_assign

        numerator, denominator = fraction(exp.lamb)
        if numerator.free_symbols:
            raise TransformException("Exponential distribution can only handle 1/expr parameters. ")

        new_var = get_unique_var()
        new_exp_assign = DistAssignment(new_var, Exponential([numerator]))
        new_assign = PolyAssignment(variable, f"({denominator}) * {new_var}")
        return new_exp_assign, new_assign

    def __transform_uniform__(self, uniform_assign):
        variable = uniform_assign.variable
        uniform: Uniform = uniform_assign.distribution

        if not self.program.variables.intersection(uniform.a.free_symbols) and not self.program.variables.intersection(
                uniform.b.free_symbols):
            return uniform_assign

        new_var = get_unique_var()
        a, b = str(uniform.a), str(uniform.b)
        new_uniform_assign = DistAssignment(new_var, Uniform([0, 1]))
        new_assign = PolyAssignment(variable, f"{a} + ({b} - ({a}))*{new_var}")
        return new_uniform_assign, new_assign
