from typing import Set
from symengine.lib.symengine_wrapper import Expr


def get_valid_values(possible_values: Set[Expr], cop: str, integer: Expr):
    if cop == "==":
        return {v for v in possible_values if bool(v == integer)}

    if cop == "<=":
        return {v for v in possible_values if bool(v <= integer)}

    if cop == ">=":
        return {v for v in possible_values if bool(v >= integer)}

    if cop == "<":
        return {v for v in possible_values if bool(v < integer)}

    if cop == ">":
        return {v for v in possible_values if bool(v > integer)}

    raise RuntimeError(f"Unknown comparison operator {cop}")
