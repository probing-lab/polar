from lark import Transformer, Tree
from utils import get_unique_var
from .exceptions import ParseException
from .tree_to_source import value_to_source


class MultiAssignTransformer(Transformer):
    """
    Transforms all multi-assignments to single assignments:

    For example
    x, y = y, x ==> _u0 = y; _u1 = x; x = _u0; y = _u1
    """

    def __init__(self, lark_parser):
        super(MultiAssignTransformer, self).__init__()
        self.lark_parser = lark_parser

    def assign(self, args):
        if len(args) == 3:
            return Tree("assign", args)
        if len(args) % 2 == 0:
            raise ParseException(f"Error in multi-assignment at line {args[0].line} col {args[0].column}")

        num_vars = int((len(args) - 1) / 2)
        if args[num_vars] != "=":
            raise ParseException(f"Error in multi-assignment at line {args[0].line} col {args[0].column}")

        assignments1 = []
        assignments2 = []
        for i in range(num_vars):
            var = args[i]
            value = args[num_vars + 1 + i]
            if var.type != "VARIABLE":
                raise ParseException(f"Error in multi-assignment at line {args[0].line} col {args[0].column}")

            new_var = get_unique_var()
            assignments1.append(self.lark_parser.parse(f"{new_var} = {value_to_source(value)}", start="assign"))
            assignments2.append(self.lark_parser.parse(f"{var} = {new_var}", start="assign"))
        return Tree("statems", assignments1 + assignments2)
