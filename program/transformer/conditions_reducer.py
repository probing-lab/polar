from typing import List, Dict

from symengine.lib.symengine_wrapper import Symbol

from .transformer import Transformer
from program import Program
from program.assignment import Assignment, PolyAssignment
from program.condition import Atom


class ConditionsReducer(Transformer):
    """
    Transforms all condition atoms in the program to the form: <variable> <comparison> <integer>
    """
    program: Program

    def execute(self, program: Program) -> Program:
        self.program = program
        self.program.initial = self.__reduce_conditions__(self.program.initial)
        self.program.loop_body = self.__reduce_conditions__(self.program.loop_body)
        return program

    def __reduce_conditions__(self, assignments: List[Assignment]):
        new_assignments = []
        store: Dict[Atom, Symbol] = {}
        for assign in assignments:
            aliases = assign.condition.reduce(store)
            for new_var, expression in aliases:
                new_assignments.append(PolyAssignment.deterministic(new_var, expression.simplify()))
            new_assignments.append(assign)
            store = self.__delete_from_store__(store, assign.variable)

        return new_assignments

    def __delete_from_store__(self, store: Dict[Atom, Symbol], variable: Symbol):
        """
        If a variable appearing in an atom gets assigned we can not use the same alias as previously
        and need to delete it from the store.
        """
        new_store = {}
        for atom, alias in store.items():
            if variable not in atom.get_free_symbols():
                new_store[atom] = alias
        return new_store
