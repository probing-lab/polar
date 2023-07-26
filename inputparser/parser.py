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

    def parse_file(self, filepath: str) -> Program:
        with open(filepath) as file:
            program = self.parse_string(file.read())
        return program

    def parse_string(self, code: str) -> Program:
        with open(GRAMMAR_FILE_PATH) as grammar_file:
            parser = Lark(
                grammar_file, transformer=ArithmeticToStringTransformer, parser="lalr"
            )
            tree = parser.parse(code)
            program = StructureTransformer().transform(tree)
        return program


def parse_program(benchmark: str) -> Program:
    return Parser().parse_file(benchmark)
