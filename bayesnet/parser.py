import os
from lark import Lark
from .transformer import NetworkTransformer

GRAMMAR_FILE_PATH = os.path.dirname(os.path.abspath(__file__)) + "/bif-syntax.lark"


class BifParser:
    """
    Parsers which takes a .bif source file and returns the program into internal representation."
    Note that this parser is stricter than the "specification" at
    http://sites.poli.usp.br/p/fabio.cozman/Research/InterchangeFormat/xmlbif02.html
        1. Sum of a CPT row must lie in the interval (1-cpt_tolerance, 1+cpt_tolerance)
        2. There is only one table/default entry per CPT allowed.
        3. The table attribute must contain all CPT entries (no zero padding is done).
        4. Non-standard blocks (i.e. all except network, variable, probability) are not allowed.
    """

    def __init__(self, cpt_tolerance: float = 0.001):
        self.cpt_tolerance = cpt_tolerance

    def parse_file(self, filepath: str):
        with open(filepath) as file:
            with open(GRAMMAR_FILE_PATH) as grammar_file:
                parser = Lark(
                    grammar_file,
                    transformer=NetworkTransformer(self.cpt_tolerance),
                    parser="lalr",
                )
                network = parser.parse(file.read())
        return network
