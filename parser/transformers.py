from lark import Transformer, Tree, Token
from utils import get_unique_var
from .exceptions import ParseException


class MultiAssignTransformer(Transformer):
    """
    Transforms all multi-assignments to single assignments:

    For example
    x, y = y, x ==> _u0 = y; _u1 = x; x = _u0; y = _u1
    """

    def assign(self, args):
        if len(args) == 3:
            return Tree("assign", args)
        if len(args) % 2 == 0:
            raise ParseException(f"Error in multi-assignment at line {args[0].line} col {args[0].column}")

        num_vars = round(len(args) / 2)
        if args[num_vars] != "=":
            raise ParseException(f"Error in multi-assignment at line {args[0].line} col {args[0].column}")
        assign_token = args[num_vars]

        assignments1 = []
        assignments2 = []
        for i in range(num_vars):
            var = args[i]
            value = args[num_vars + 1 + i]
            if var.type != "VARIABLE":
                raise ParseException(f"Error in multi-assignment at line {args[0].line} col {args[0].column}")
            new_var = Token(b"VARIABLE", get_unique_var())
            assignments1.append(Tree("assign", [new_var, assign_token, value]))
            assignments2.append(Tree("assign", [var, assign_token, new_var]))
        return Tree("statems", assignments1 + assignments2)


class DistributionsTransformer(Transformer):
    """
    Transforms all Normal distributions and Uniform distributions into normalized form

    For example
    x = Normal(y**2,1) ==> _u = Normal(0,1); x = y**2 + _u
    x = Uniform(y**2, z) ==> _u = Uniform(0,1); x = y**2 + (z - y**2)*_u
    """

    def __transform_normal(self, var, params, original_sub_tree):
        if len(params) != 2:
            raise ParseException(f"Error for normal distribution at line {var.line} col {var.column}")
        mu = params[0]
        if mu == "0":
            return original_sub_tree

        new_var = Token(b"VARIABLE", get_unique_var())
        # _u = Normal(0,1)
        dist_assign = Tree("assign", [
            new_var, Token(b"ASSIGN", "="),
            Tree("dist", [Token(b"DIST_NAME", "Normal"), Token(b"NUMBER", "0"), params[1]])])
        # var = mu + _u
        var_assign = Tree("assign", [var, Token(b"ASSIGN", "="), Tree("poly", [mu, Token(b"PLUS", "+"), new_var])])

        return Tree("statems", [dist_assign, var_assign])

    def __transform_uniform(self, var, params, original_sub_tree):
        if len(params) != 2:
            raise ParseException(f"Error for uniform distribution at line {var.line} col {var.column}")
        a = params[0]
        b = params[1]
        if a == "0" and b == "1":
            return original_sub_tree

        new_var = Token(b"VARIABLE", get_unique_var())
        # _u = Uniform(0,1)
        dist_assign = Tree("assign", [
            new_var, Token(b"ASSIGN", "="),
            Tree("dist", [Token(b"DIST_NAME", "Uniform"), Token(b"NUMBER", "0"), Token(b"NUMBER", "1")])])
        # var = a + (b-a)*_u
        var_assign = Tree("assign", [
            var, Token(b"ASSIGN", "="), Tree("poly", [
                a, Token(b"PLUS", "+"), Token(b"BOPEN", "("), b, Token(b"MINUS", "-"), a, Token(b"BCLOSE", ")"),
                Token(b"MULT", "*"), new_var])])
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
            return self.__transform_normal(var, dist_params, original_sub_tree)
        elif dist_name == "Uniform":
            return self.__transform_uniform(var, dist_params, original_sub_tree)

        return original_sub_tree
