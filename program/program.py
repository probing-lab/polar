from typing import Optional
from symengine.lib.symengine_wrapper import sympify
from .type import Type, Finite
from utils import indent_string


class Program:
    children = ["initial", "loop_body"]

    def __init__(self, types, variables, original_variables, initial, loop_guard, loop_body, is_probabilistic):
        self.typedefs = {}
        self.finite_variables = []
        self.dist_variables = []
        self.func_variables = []
        self.add_types(types)
        self.original_variables = {sympify(v) for v in original_variables}
        self.variables = {sympify(v) for v in variables}
        self.symbols = set()
        self.initial = initial
        self.loop_guard = loop_guard
        self.loop_body = loop_body
        self.abstracted_const_store = {}
        self.is_probabilistic = is_probabilistic # set by the parsers: true iff the program contains proper probabilistic constructs
        self.original_loop_guard = None  # initialized by the conditions-normalizer
        self.var_to_index = {}           # initialized by info transformer
        self.index_to_var = {}           # initialized by info transformer
        self.dependency_info = {}        # initialized by info transformer
        self.mc_variables = set()        # initialize by info transformer
        self.non_mc_variables = set()    # initialize by info transformer

    def add_type(self, t: Type):
        if t is not None:
            self.typedefs[t.variable] = t
        if isinstance(t, Finite) and t.variable not in self.finite_variables:
            self.finite_variables.append(t.variable)

    def add_types(self, ts: [Type]):
        for t in ts:
            self.add_type(t)

    def get_type(self, variable) -> Optional[Type]:
        return self.typedefs.get(variable)

    def is_iteration_dependent(self, variable):
        return self.dependency_info[variable].iteration_dependent

    def is_dependent(self, var1, var2):
        return var1 in self.dependency_info[var2].dependencies

    def is_dependent_vars(self, variables1, variables2):
        for v1 in variables1:
            if any([self.is_dependent(v1, v2) for v2 in variables2]):
                return True
        return False

    def __str__(self):
        typedefs = "\n".join([str(t) for t in self.typedefs.values()])
        initial = "\n".join([str(i) for i in self.initial])
        body = "\n".join([str(b) for b in self.loop_body])

        string = ""
        if self.typedefs:
            string = f"types\n{indent_string(typedefs, 4)}\nend\n"

        string += f"{initial}\nwhile {str(self.loop_guard)}:\n{indent_string(body, 4)}\nend"

        if len(self.abstracted_const_store) > 0:
            abstractions = "\n".join([f"{prob} = P({cond})" for prob, cond in self.abstracted_const_store.items()])
            string += f"\nwhere\n{indent_string(abstractions, 4)}"

        return string
