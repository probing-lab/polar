from lark import Lark
from .transformers import MultiAssignTransformer, DistributionsTransformer

GRAMMAR_FILE_PATH = "parser/syntax.lark"


class Parser:

    def parse_file(self, filepath: str):
        with open(filepath) as file:
            with open(GRAMMAR_FILE_PATH) as grammar_file:
                lark_parser = Lark(grammar_file)
                tree = lark_parser.parse(file.read())
                tree = MultiAssignTransformer().transform(tree)
                tree = DistributionsTransformer().transform(tree)
                print(tree.pretty())
                return tree
