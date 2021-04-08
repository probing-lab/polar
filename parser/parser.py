from lark import Lark

from program import Program
from .multi_assign_transformer import MultiAssignTransformer
from .distributions_transformer import DistributionsTransformer
from .categorical_transformer import CategoricalTransformer
from .structure_transformer import StructureTransformer
from .arithmetic_transformer import ArithmeticToStringTransformer

GRAMMAR_FILE_PATH = "parser/syntax.lark"


class Parser:

    def parse_file(self, filepath: str) -> Program:
        with open(filepath) as file:
            with open(GRAMMAR_FILE_PATH) as grammar_file:
                parser = Lark(grammar_file, transformer=ArithmeticToStringTransformer, parser="lalr")
                tree = parser.parse(file.read())
                tree = MultiAssignTransformer(parser).transform(tree)
                tree = CategoricalTransformer(parser).transform(tree)
                tree = DistributionsTransformer(parser).transform(tree)
                program = StructureTransformer().transform(tree)
        return program
