from lark import Lark

from program import Program
from .structure_transformer import StructureTransformer
from .arithmetic_transformer import ArithmeticToStringTransformer

GRAMMAR_FILE_PATH = "inputparser/syntax.lark"


class Parser:
    """
    Parsers which takes a .prob source file and returns the program in a form such that it can be used further.
    """

    def parse_file(self, filepath: str, transform_categoricals=False) -> Program:
        with open(filepath) as file:
            with open(GRAMMAR_FILE_PATH) as grammar_file:
                parser = Lark(grammar_file, transformer=ArithmeticToStringTransformer, parser="lalr")
                tree = parser.parse(file.read())
                program = StructureTransformer(transform_categoricals).transform(tree)
        return program
