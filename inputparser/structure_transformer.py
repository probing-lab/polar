from lark import Transformer, Tree, Token
from program import Program
from program.assignment import DistAssignment, PolyAssignment
from program.condition import Condition, Atom, Not, And, Or, TrueCond, FalseCond
from program.distribution import distribution_factory, Distribution, Categorical
from program.ifstatem import IfStatem
from program.type import type_factory, Type
from utils import get_unique_var
from .exceptions import ParseException


class StructureTransformer(Transformer):
    """
    Lark transformer which transform the parse tree returned by lark into our own representations
    """
    def __init__(self):
        super().__init__()
        self.program_variables = set()

    def program(self, args) -> Program:
        """
        Constructs the most outer data wrapper
        """
        tree = Tree("program", args)
        td = list(tree.find_data("typedefs"))
        i = list(tree.find_data("initial")).pop()
        lg = list(tree.find_data("loop_guard")).pop()
        lb = list(tree.find_data("loop_body")).pop()

        typedefs = td[0].children if td else []
        initial = i.children[0] if i.children else []
        loop_guard = lg.children[0]
        loop_body = lb.children[0]

        return Program(typedefs, self.program_variables, initial, loop_guard, loop_body)

    def dist(self, args):
        dist_name = str(args[0])
        parameters = [str(p) for p in args[1:]]
        return distribution_factory(dist_name, parameters)

    def if_statem(self, args) -> IfStatem:
        conditions = [a for a in args if isinstance(a, Condition)]
        branches = [a for a in args if not isinstance(a, Condition)]
        else_branch = None
        if len(branches) > len(conditions):
            else_branch = branches.pop()
        return IfStatem(conditions, branches, else_branch)

    def typedef(self, args) -> Type:
        var = str(args[0])
        name = str(args[1].children[0])
        params = [str(a) for a in args[1].children[1:]]
        return type_factory(name, params, var)

    def statems(self, args) -> []:
        statements = []
        for a in args:
            if type(a) is list:
                statements += a
            else:
                statements.append(a)
        return statements

    def atom(self, args) -> Condition:
        if len(args) == 1 and args[0].type == "TRUE":
            return TrueCond()
        if len(args) == 1 and args[0].type == "FALSE":
            return FalseCond()

        poly1 = str(args[0])
        cop = str(args[1])
        poly2 = str(args[2])
        return Atom(poly1, cop, poly2)

    def condition(self, args) -> Condition:
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

    def assign(self, args):
        if len(args) > 3:
            return self.__assign__simult__(args)
        var = str(args[0])
        self.program_variables.add(var)
        value = args[2]
        if isinstance(value, Distribution):
            return DistAssignment(var, value)
        elif isinstance(value, Tree) and value.data == "categorical":
            return self.__assign__categorical__(args)
        else:
            return PolyAssignment(var, str(value))

    def __assign__categorical__(self, args):
        """
        Helper function to transform the syntactic sugar categorical assignment
        x = v1 {p1} v2 {p2} ...
        into an if-statement
        """
        var = args[0]
        assigns = args[2].children[0::2]
        params = args[2].children[1::2]
        if len(params) < len(assigns):
            last_param = f"1-{'-'.join(params)}"
            params.append(last_param)

        cat_var = get_unique_var()
        cat_assign = DistAssignment(cat_var, Categorical(params))
        conditions = []
        assignments = []
        for i in range(len(assigns)):
            conditions.append(Atom(cat_var, "==", str(i)))
            assignments.append([PolyAssignment(var, assigns[i])])
        return [cat_assign, IfStatem(conditions, assignments, mutually_exclusive=True)]

    def __assign__simult__(self, args):
        """
        Helper function to transform
        """
        if len(args) % 2 == 0:
            raise ParseException(f"Error in simultaneous assignment at line {args[0].line} col {args[0].column}")

        num_vars = int((len(args) - 1) / 2)
        if args[num_vars] != "=":
            raise ParseException(f"Error in simultaneous assignment at line {args[0].line} col {args[0].column}")

        assignments1 = []
        assignments2 = []
        for i in range(num_vars):
            var = args[i]
            self.program_variables.add(var)
            value = args[num_vars + 1 + i]
            if var.type != "VARIABLE":
                raise ParseException(f"Error in simultaneous assignment at line {args[0].line} col {args[0].column}")

            new_var = get_unique_var()
            assignments1.append(self.assign([Token(b"VARIABLE", new_var), Token(b"ASSIGN", "="), value]))
            assignments1.append(self.assign([var, Token(b"ASSIGN", "="), new_var]))
        return assignments1 + assignments2
