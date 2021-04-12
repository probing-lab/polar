
def indent_string(string: str, indent: int):
    lines = string.split("\n")
    lines = [(" " * indent) + line for line in lines]
    return "\n".join(lines)
