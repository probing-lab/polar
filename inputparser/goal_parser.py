from .exceptions import ParseException
from sympy import sympify

MOMENT = "MOMENT"
TAIL_BOUND = "TAIL_BOUND"


class GoalParser:

    @staticmethod
    def parse(goal: str):
        if len(goal) < 3 or goal[1] != "(" or goal[-1] != ")":
            raise ParseException(f"Malformed goal {goal}")

        between_brackets = goal[2:-1].strip()
        if goal[0] == "E":
            return GoalParser.__parse_moment__(between_brackets)
        if goal[0] == "P":
            return GoalParser.__parse_tail_bound__(between_brackets)
        raise ParseException(f"Unknown goal {goal}")

    @staticmethod
    def __parse_moment__(between_brackets: str):
        return MOMENT, [sympify(between_brackets)]

    @staticmethod
    def __parse_tail_bound__(between_brackets: str):
        if between_brackets.find(">=") < 0:
            raise ParseException(f"Error in tail bound goal {between_brackets}")
        tokens = between_brackets.split(">=")
        if len(tokens) != 2:
            raise ParseException(f"Error in tail bound goal {between_brackets}")
        tokens = [sympify(t.strip()) for t in tokens]
        return TAIL_BOUND, tokens
