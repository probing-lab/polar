import os
from lark import Lark
from transformer import NetworkTransformer

GRAMMAR_FILE_PATH = os.path.dirname(os.path.abspath(__file__)) + "/bif-syntax.lark"
BIF_REPO = os.path.dirname(os.path.abspath(__file__)) + "/repo"


class BifParser:
    """
    Parsers which takes a .bif source file and returns the program in a form such that it can be used further.
    """

    def parse_file(self, filepath: str):
        with open(filepath) as file:
            with open(GRAMMAR_FILE_PATH) as grammar_file:
                parser = Lark(grammar_file, transformer=NetworkTransformer(), parser="lalr")
                network = parser.parse(file.read())
                print(network.print_pretty())


BifParser().parse_file(BIF_REPO + "/testcases/asia.bif")
