from typing import Optional

from diofant import sympify

from .type import Type
from utils import indent_string


class Program:
    children = ["initial", "loop_body"]

    def __init__(self, types, variables, initial, loop_guard, loop_body):
        self.typedefs = {}
        self.add_types(types)
        self.variables = {sympify(v) for v in variables}
        self.symbols = set()
        self.initial = initial
        self.loop_guard = loop_guard
        self.loop_body = loop_body

    def add_type(self, t: Type):
        self.typedefs[t.expression] = t

    def add_types(self, ts: [Type]):
        for t in ts:
            self.add_type(t)

    def get_type(self, expression) -> Optional[Type]:
        return self.typedefs.get(expression)

    def __str__(self):
        typedefs = "\n".join([str(t) for t in self.typedefs.values()])
        if isinstance(self.initial, dict):
            initial = "\n".join([str(self.initial[i]) for i in self.initial])
        else:
            initial = "\n".join([str(i) for i in self.initial])
        if isinstance(self.loop_body, dict):
            body = "\n".join([str(self.loop_body[b]) for b in self.loop_body])
        else:
            body = "\n".join([str(b) for b in self.loop_body])

        string = ""
        if self.typedefs:
            string = f"types\n{indent_string(typedefs, 4)}\nend\n"

        string += f"{initial}\nwhile {str(self.loop_guard)}:\n{indent_string(body, 4)}\nend"
        return string
