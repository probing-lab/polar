from lark import Transformer, Tree
from program import Program
from program.assignment import DistAssignment, PolyAssignment
from program.condition import Condition, Atom, Not, And, Or
from program.distribution import distribution_factory, Distribution
from program.ifstatem import IfStatem
from program.type import Finite
from .exceptions import ParseException


class StructureTransformer(Transformer):

    def program(self, args):
        tree = Tree("program", args)
        td = list(tree.find_data("typedefs"))
        i = list(tree.find_data("initial")).pop()
        lg = list(tree.find_data("loop_guard")).pop()
        lb = list(tree.find_data("loop_body")).pop()

        typedefs = td[0].children if td else []
        initial = i.children[0] if i.children else []
        loop_guard = lg.children
        loop_body = lb.children[0]

        return Program(typedefs, initial, loop_guard, loop_body)

    def dist(self, args):
        dist_name = str(args[0])
        parameters = [str(p) for p in args[1:]]
        return distribution_factory(dist_name, parameters)

    def assign(self, args):
        var = str(args[0])
        value = args[2]
        if isinstance(value, Distribution):
            return DistAssignment(var, value)
        else:
            return PolyAssignment(var, str(value))

    def statems(self, args):
        statements = []
        for a in args:
            if type(a) is list:
                statements += a
            else:
                statements.append(a)

        return statements

    def atom(self, args):
        poly1 = str(args[0])
        cop = str(args[1])
        poly2 = str(args[2])
        return Atom(poly1, cop, poly2)

    def condition(self, args):
        if len(args) == 1:
            return args[0]
        if len(args) == 2:
            cond = args[1]
            return Not(cond)
        if len(args) == 3:
            cond1 = args[0]
            binop = str(args[1])
            cond2 = args[2]
            if binop == "&&":
                return And(cond1, cond2)
            elif binop == "||":
                return Or(cond1, cond2)
        raise ParseException("Error in condition")

    def if_statem(self, args):
        conditions = [a for a in args if isinstance(a, Condition)]
        branches = [a for a in args if not isinstance(a, Condition)]
        else_branch = None
        if len(branches) > len(conditions):
            else_branch = branches.pop()
        return IfStatem(conditions, branches, else_branch)

    def typedef(self, args):
        var = str(args[0])
        type_name = str(args[1].children[0])
        if type_name != "Finite":
            raise ParseException("Only type 'Finite' is supported")
        type_params = args[1].children[1:]
        if len(type_params) != 2:
            raise ParseException("Type 'Finite' requires two parameters")
        lower = str(type_params[0])
        upper = str(type_params[1])
        return Finite(var, lower, upper)
