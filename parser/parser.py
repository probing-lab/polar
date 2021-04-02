from lark import Lark


GRAMMAR_FILE_PATH = "parser/syntax.lark"


class Parser:

    def parse_file(self, filepath: str):
        with open(filepath) as file:
            with open(GRAMMAR_FILE_PATH) as grammar_file:
                lark_parser = Lark(grammar_file)
                tree = lark_parser.parse(file.read())
                return tree
