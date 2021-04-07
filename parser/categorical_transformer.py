from lark import Transformer, Tree
from utils import get_unique_var
from .tree_to_source import value_to_source


class CategoricalTransformer(Transformer):
    """
    Transforms the shortcut representation for categoricals in its expanded form with if-statements

    For example
    x = a {0.5} b -> _u = Categorical(0.5, 1-0.5); if _u == 0: x = a else if _u == 1: x = b end
    """

    def __init__(self, lark_parser):
        super(CategoricalTransformer, self).__init__()
        self.lark_parser = lark_parser

    def assign(self, args):
        original_sub_tree = Tree("assign", args)
        if not hasattr(args[2], "data") or args[2].data != "categorical":
            return original_sub_tree
        var = args[0]
        assigns = args[2].children[0::2]
        params = args[2].children[1::2]
        if len(params) < len(assigns):
            last_param = f"1-{'-'.join(params)}"
            params.append(last_param)

        cat_var = get_unique_var()
        cat_assign = self.lark_parser.parse(f"{cat_var} = Categorical({','.join(params)})", start="assign")
        if_string = ""
        for i in range(len(assigns)):
            if_string += f"{'else ' if i > 0 else ''}if {cat_var} == {i}:\n{var} = {value_to_source(assigns[i])}\n"
        if_string += "end"
        if_statem = self.lark_parser.parse(if_string, start="if_statem")

        return Tree("statems", [cat_assign, if_statem])
