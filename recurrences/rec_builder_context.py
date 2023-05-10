from typing import Set, Dict, TYPE_CHECKING
from symengine.lib.symengine_wrapper import Symbol, Expr

if TYPE_CHECKING:
    from program.assignment import FunctionalAssignment


class RecBuilderContext:
    """
    Instances of this class are used to store information during the process of building a recurrence
    for a monomial. When substituting (the expected value of) an assignment, most assignment are local, meaning
    they don't need any information of what happened before. However, for instance, FunctionalAssignments are
    not substituted but their variables are handled simultaneously with the dist assignment of their parameters.
    Hence, the FunctionalAssignments will change the context and the DistAssignments require the context of what
    happened before to correctly evaluate/substitute.
    """

    # maps a variable v to their triggers, if a trigger occurs in a monomial, then get_moment of the assignment
    # of v will be called on this monomial, even if v doesn't occur in the monomial.
    triggers: Dict[Symbol, Set[Symbol]]
    # maps variables to their functional assignments
    func_assignments: Dict[Symbol, "FunctionalAssignment"]
    # Maps distribution variables v to functional variables that use v as a parameter
    dist_var_dependent_func_vars: Dict[Symbol, Set[Symbol]]

    def __init__(self):
        self.triggers = {}
        self.func_assignments = {}
        self.dist_var_dependent_func_vars = {}

    def add_trigger(self, variable: Symbol, trigger: Symbol):
        if variable in self.triggers:
            self.triggers[variable].add(trigger)
        else:
            self.triggers[variable] = {trigger}

    def add_func_assignments(self, fassign: "FunctionalAssignment"):
        self.func_assignments[fassign.variable] = fassign
        if fassign.argument in self.dist_var_dependent_func_vars:
            self.dist_var_dependent_func_vars[fassign.argument].add(fassign.variable)
        else:
            self.dist_var_dependent_func_vars[fassign.argument] = {fassign.variable}

    def var_has_triggers_in_expr(self, variable: Symbol, poly: Expr):
        if variable not in self.triggers:
            return False
        return bool(self.triggers[variable] & poly.free_symbols)
