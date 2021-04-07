from lark import Transformer, Tree
from utils import get_unique_var
from .exceptions import ParseException
from .tree_to_source import value_to_source


class DistributionsTransformer(Transformer):
    """
    Transforms all Normal distributions and Uniform distributions into normalized form

    For example
    x = Normal(y**2,1) ==> _u = Normal(0,1); x = y**2 + _u
    x = Uniform(y**2, z) ==> _u = Uniform(0,1); x = y**2 + (z - y**2)*_u
    """

    def __init__(self, lark_parser):
        super(DistributionsTransformer, self).__init__()
        self.lark_parser = lark_parser

    def __transform_normal__(self, var, params, original_sub_tree):
        if len(params) != 2:
            raise ParseException(f"Error for normal distribution at line {var.line} col {var.column}")
        mu = params[0]
        if mu == "0":
            return original_sub_tree

        new_var = get_unique_var()
        sigma = value_to_source(params[1])
        mu = value_to_source(mu)
        dist_assign = self.lark_parser.parse(f"{new_var} = Normal(0,{sigma})", start="assign")
        var_assign = self.lark_parser.parse(f"{var} = {mu} + {new_var}", start="assign")
        return Tree("statems", [dist_assign, var_assign])

    def __transform_uniform__(self, var, params, original_sub_tree):
        if len(params) != 2:
            raise ParseException(f"Error for uniform distribution at line {var.line} col {var.column}")
        a = params[0]
        b = params[1]
        if a == "0" and b == "1":
            return original_sub_tree

        new_var = get_unique_var()
        a = value_to_source(a)
        b = value_to_source(b)
        dist_assign = self.lark_parser.parse(f"{new_var} = Uniform(0,1)", start="assign")
        var_assign = self.lark_parser.parse(f"{var} = {a} + ({b} - ({a}))*{new_var}", start="assign")
        return Tree("statems", [dist_assign, var_assign])

    def assign(self, args):
        original_sub_tree = Tree("assign", args)
        if len(args) != 3:
            raise ParseException(f"Error in assignment at line {args[0].line} col {args[0].column}")
        var = args[0]
        value = args[2]
        if not hasattr(value, "data") or value.data != "dist":
            return original_sub_tree
        dist_name = value.children[0]
        dist_params = value.children[1:]

        if dist_name == "Normal":
            return self.__transform_normal__(var, dist_params, original_sub_tree)
        elif dist_name == "Uniform":
            return self.__transform_uniform__(var, dist_params, original_sub_tree)

        return original_sub_tree
