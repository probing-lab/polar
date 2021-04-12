from utils import indent_string


class Program:

    children = ["initial", "loop_body"]

    def __init__(self, typedefs, initial, loop_guard, loop_body):
        self.typedefs = typedefs
        self.initial = initial
        self.loop_guard = loop_guard
        self.loop_body = loop_body

    def __str__(self):
        typedefs = "\n".join([str(t) for t in self.typedefs])
        initial = "\n".join([str(i) for i in self.initial])
        body = "\n".join([str(b) for b in self.loop_body])

        string = ""
        if self.typedefs:
            string = f"types\n{indent_string(typedefs, 4)}\nend\n"

        string += f"{initial}\nwhile {str(self.loop_guard)}:\n{indent_string(body, 4)}\nend"
        return string
