from lark import Transformer


class ArithmeticToStringTransformer(Transformer):
    """
    Lark Transformer which converts all tokens involved in arithmetic expression right back to strings.
    The tokens result from parsing the text through the corresponding grammar, but we need it back in
    string form so the CAS can read it.
    """

    @staticmethod
    def arithm(args):
        result = "".join([str(a) for a in args])
        return result
