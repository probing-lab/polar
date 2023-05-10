import string, random


def indent_string(string: str, indent: int):
    lines = string.split("\n")
    lines = [(" " * indent) + line for line in lines]
    return "\n".join(lines)


def random_string(length):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))
