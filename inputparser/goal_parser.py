from .exceptions import ParseException
from symengine.lib.symengine_wrapper import sympify

MOMENT = "MOMENT"
TAIL_BOUND_UPPER = "TAIL_BOUND_UPPER"
TAIL_BOUND_LOWER = "TAIL_BOUND_LOWER"


class GoalParser:

    @staticmethod
    def parse(goal: str):
        # TODO: makes this nice
        if goal.endswith(" >= ?") or goal.endswith(" <= ?"):
            goal = goal[0:-5]

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
        if between_brackets.find(">=") >= 0:
            bound_type = TAIL_BOUND_UPPER
            split_str = ">="
        elif between_brackets.find(">") >= 0:
            bound_type = TAIL_BOUND_LOWER
            split_str = ">"
        else:
            raise ParseException(f"Error in tail bound goal {between_brackets}")
        tokens = between_brackets.split(split_str)
        if len(tokens) != 2:
            raise ParseException(f"Error in tail bound goal {between_brackets}")
        tokens = [sympify(t.strip()) for t in tokens]
        return bound_type, tokens
