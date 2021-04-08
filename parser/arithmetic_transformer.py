from lark import Transformer


class ArithmeticToStringTransformer(Transformer):

    @staticmethod
    def arithm(args):
        result = "".join([str(a) for a in args])
        return result
