from functools import reduce
from sympy import Add, Function, Interval, Mul, expand, simplify


class Expexted(Function):
    @classmethod
    def eval(cls, arg):
        arg = (expand(arg))
        if isinstance(arg, Add):
            return Add(*[cls(term) for term in arg.args])
        if arg.is_number:
            return arg
        # Do not distribute over multiplication
        if isinstance(arg, Mul):
            # collect the numbers:
            nrs,rest = reduce(lambda numbers_rest, v: (numbers_rest[0]+[v], numbers_rest[1]) if v.is_number else (numbers_rest[0], numbers_rest[1]+[v]) , arg.args, ([],[]))
            if len(nrs) == 0:
                return None
            return Mul(*nrs,cls(Mul(*rest)))
        return None