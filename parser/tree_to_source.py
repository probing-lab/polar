from lark import Token


def value_to_source(value):
    if isinstance(value, str):
        return value

    if isinstance(value, Token):
        return str(value)

    if value.data == "dist":
        dist_name = str(value.children[0])
        params = value.children[1:]
        source = f"{dist_name}({','.join(params)})"
        return source

    raise RuntimeError("Can only convert tokens and distributions to source")
