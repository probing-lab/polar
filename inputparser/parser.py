import os
from lark import Lark

from program import Program
from .structure_transformer import StructureTransformer
from .arithmetic_transformer import ArithmeticToStringTransformer

GRAMMAR_FILE_PATH = os.path.dirname(__file__) + "/syntax.lark"


class Parser:
    """
    Parsers which takes a .prob source file and returns the program in a form such that it can be used further.
    """

    def parse_file(self, filepath: str, transform_categoricals=False) -> Program:
        with open(filepath) as file:
            program = self.parse_string(file.read(), transform_categoricals)
        return program

    def parse_string(self, code: str, transform_categoricals=False) -> Program:
        with open(GRAMMAR_FILE_PATH) as grammar_file:
            parser = Lark(
                grammar_file, transformer=ArithmeticToStringTransformer, parser="lalr"
            )
            tree = parser.parse(code)
            program = StructureTransformer(transform_categoricals).transform(tree)
        return program


def parse_program(benchmark: str, transform_categorial=False) -> Program:
    return Parser().parse_file(benchmark, transform_categorial)
