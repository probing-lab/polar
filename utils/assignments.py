from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from program.assignment import Assignment
from .identifiers import get_unique_var


def make_assigns_parallel(assigns: ["Assignment"]):
    from program.assignment import PolyAssignment

    if len(assigns) <= 1:
        return assigns

    substitutions = {}
    tmp_assigns = []
    for assign in assigns:
        tmp_var = get_unique_var("t")
        substitutions[assign.variable] = tmp_var
        tmp_assigns.append(PolyAssignment.deterministic(tmp_var, assign.variable))
    for assign in assigns:
        assign.subs(substitutions)
    return tmp_assigns + assigns
