from lark import Lark
from .multi_assign_transformer import MultiAssignTransformer
from .distributions_transformer import DistributionsTransformer
from .categorical_transformer import CategoricalTransformer

GRAMMAR_FILE_PATH = "parser/syntax.lark"


class Parser:

    def parse_file(self, filepath: str):
        with open(filepath) as file:
            with open(GRAMMAR_FILE_PATH) as grammar_file:
                lark_parser = Lark(grammar_file)
                tree = lark_parser.parse(file.read())
                tree = MultiAssignTransformer(lark_parser).transform(tree)
                tree = CategoricalTransformer(lark_parser).transform(tree)
                tree = DistributionsTransformer(lark_parser).transform(tree)
                print(tree.pretty())
                return tree
