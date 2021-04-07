from lark import Transformer
from program.assignment import DistAssignment, PolyAssignment
from program.condition import Condition
from program.distribution import distribution_factory, Distribution
from program.type import Finite
from .exceptions import ParseException


class StructureTransformer(Transformer):

    def dist(self, args):
        dist_name = str(args[0])
        parameters = [str(p) for p in args[1:]]
        return distribution_factory(dist_name, parameters)

    def assign(self, args):
        var = str(args[0])
        value = args[2]
        if isinstance(value, Distribution):
            return DistAssignment(var, value)
        else:
            return PolyAssignment(var, str(value))

    def statems(self, args):
        statements = []
        for a in args:
            if type(a) is list:
                statements += a
            else:
                statements.append(a)

        return statements

    def condition(self, args):
        # TODO
        return Condition(args)

    def typedef(self, args):
        var = str(args[0])
        type_name = str(args[1].children[0])
        if type_name != "Finite":
            raise ParseException("Only type 'Finite' is supported")
        type_params = args[1].children[1:]
        if len(type_params) != 2:
            raise ParseException("Type 'Finite' requires two parameters")
        lower = str(type_params[0])
        upper = str(type_params[1])
        return Finite(var, lower, upper)
