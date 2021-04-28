from dataclasses import dataclass
from typing import List, Set, Dict, Tuple
from symengine.lib.symengine_wrapper import Expr, Symbol

from program import Program
from program.assignment import Assignment
from program.condition import TrueCond
from program.type import Type, Finite
from type_inference import Typer
from .exceptions import TyperNotApplicableException


@dataclass
class Status:
    """
    Describes the status of one variable in the fixedpoint computation
    """
    values: Set[Expr]   # All possible values the variable can assume
    has_changed: bool   # Flag the check whether the values set has changed within the last iteration
    has_failed: bool    # Flat to check whether infering a finite type has failed
    is_locked: bool     # Flag to check whether the status has been locked, because the typing of the variable failed or the type has been fixed by user.


class FiniteFixedPointTyper(Typer):
    """
    This typer performs a fixedpoint computation to infer that variables are of finite type, meaning they
    only take finitely many values throughout the computation.
    The typer requires that the passed program is flattened, meaning it does not contain any if-statements.
    Moreover, every variable is assumed to have only a single assignment.
    """

    state: Dict[Symbol, Status]
    program: Program

    # After this many iterations. Variables which change are considered to have failed.
    iterations: int

    def __init__(self, iterations=10):
        self.iterations = iterations

    def infer_types(self, program: Program) -> List[Type]:
        self.program = program
        self.__check_applicability__()
        self.__initialize_state__()

        # Evolve the state at most iteration number of times
        for i in range(self.iterations):
            self.__progress__()
            if self.__fixedpoint_reached__():
                break

        # Now, fail all variables which change in one iteration until a fixedpoint is reached.
        # In the worst case all variables fail and a fixedpoint is reached.
        while not self.__fixedpoint_reached__():
            self.__fail_changed_variables__()
            self.__progress__()

        return self.__extract_types__()

    def __check_applicability__(self):
        """
        This typer is only applicable if there are no conditions in the initialization part
        """
        for assign in self.program.initial:
            if type(assign.condition) != TrueCond:
                raise TyperNotApplicableException("For type inference no conditions are allowed in initial part")

    def __progress__(self):
        """
        Evolves the state for one loop iteration, by computing all possible new values for all variables
        """
        for assign in self.program.loop_body:
            if not self.state[assign.variable].is_locked:
                new_values = self.__get_values_for_assign__(assign)
                self.__update_variable_status__(assign.variable, new_values)
            else:
                self.state[assign.variable].has_changed = False

    def __update_variable_status__(self, variable, new_values):
        """
        Updates the status of the given variable assuming it can take values from new_values
        in the current iteration.
        """
        if not new_values:
            # if new_values is false, variable depends on a failed variable
            self.__fail_variable__(variable)
        else:
            if new_values.issubset(self.state[variable].values):
                self.state[variable].has_changed = False
            else:
                self.state[variable].values |= new_values
                self.state[variable].has_changed = True

    def __fail_variable__(self, variable):
        self.state[variable].has_failed = True
        self.state[variable].is_locked = True
        self.state[variable].has_changed = True

    def __initialize_state__(self):
        """
        Initializes the state according to type definitions and initial assignments
        """
        self.state = {}

        # type definitions are assumed to be true and therefore locked.
        for var, var_type in self.program.typedefs.items():
            if isinstance(var_type, Finite):
                self.state[var] = Status(var_type.values, has_changed=False, is_locked=True, has_failed=False)

        # For variables with initial assignments, the initial state is given by the possible values it
        # can take ofter the initialization part
        for assign in self.program.initial:
            if assign.variable not in self.state:
                values = self.__get_values_for_assign__(assign)
                if values:
                    self.state[assign.variable] = Status(
                        values, has_changed=True, is_locked=False, has_failed=False)
                else:
                    self.state[assign.variable] = Status(
                        set(), has_changed=True, is_locked=True, has_failed=True)

        # For a variable v with no type definition and no initial assignment, the initial value is given
        # by the symbol v0 or by the empty set if v0 isn't used anyway. That's the case if v isn't used
        # before its assignment in the loop body.
        running_symbols = set()
        for assign in self.program.loop_body:
            running_symbols |= assign.get_free_symbols()
            if assign.variable not in self.state:
                values = {Symbol(str(assign.variable) + "0")} if assign.variable in running_symbols else set()
                self.state[assign.variable] = Status(values, has_changed=True, is_locked=False, has_failed=False)

    def __get_values_for_assign__(self, assign: Assignment):
        """
        Returns all possible values an assignment can assign with respect to the current state.
        """
        support = assign.get_support()
        if type(support) is Tuple:
            return False

        values = set()
        for expr in support:
            values_expr = self.__get_values_for_expr__(expr)
            if not values_expr:
                return False
            values |= values_expr
        return values

    def __get_values_for_expr__(self, expr: Expr):
        """
        Computes all possible values an expression can take with respect to the current state.
        """
        variables = expr.free_symbols.difference(self.program.symbols)
        result = {expr}
        for var in variables:
            if self.state[var].has_failed:
                return False
            result = {expr.xreplace({var: value}) for expr in result for value in self.state[var].values}

        return result

    def __fail_changed_variables__(self):
        for variable, status in self.state.items():
            if status.has_changed:
                self.__fail_variable__(variable)

    def __fixedpoint_reached__(self):
        return all([not s.has_changed for s in self.state.values()])

    def __extract_types__(self):
        types = []
        for variable, status in self.state.items():
            if not status.has_failed:
                types.append(Finite(status.values, variable))
        return types
