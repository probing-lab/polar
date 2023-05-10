from .exceptions import ParseException
from symengine.lib.symengine_wrapper import sympify
import re

MOMENT = "MOMENT"
CUMULANT = "CUMULANT"
CENTRAL = "CENTRAL"
TAIL_BOUND_UPPER = "TAIL_BOUND_UPPER"
TAIL_BOUND_LOWER = "TAIL_BOUND_LOWER"


class GoalParser:
    @staticmethod
    def parse(goal: str):
        if goal.find("(") < 0 and goal.find(")") < 0:
            goal = f"E({goal})"

        if len(goal) < 4:
            raise ParseException(f"Malformed goal {goal}")

        if goal[0] == "E":
            return GoalParser._parse_moment(goal)
        if goal[0] == "k":
            return GoalParser._parse_moment_relative(goal, CUMULANT)
        if goal[0] == "c":
            return GoalParser._parse_moment_relative(goal, CENTRAL)
        if goal[0] == "P":
            return GoalParser._parse_tail_bound(goal)
        raise ParseException(f"Unknown goal {goal}")

    @staticmethod
    def _parse_moment_relative(goal: str, kind):
        bracket_pos = goal.find("(")
        if bracket_pos < 0 or goal[-1] != ")":
            raise ParseException(f"Malformed goal {goal}")
        try:
            number = int(goal[1:bracket_pos])
            between_brackets = goal[bracket_pos + 1 : -1].strip()
            return kind, [number, sympify(between_brackets)]
        except Exception:
            raise ParseException(f"Malformed goal {goal}")

    @staticmethod
    def _parse_moment(goal: str):
        if goal[1] != "(" or goal[-1] != ")":
            raise ParseException(f"Malformed goal {goal}")
        between_brackets = goal[2:-1].strip()
        return MOMENT, [sympify(between_brackets)]

    @staticmethod
    def _parse_tail_bound(goal: str):
        match = re.search(
            "^P\\(([0-9a-zA-Z*/.+\\-)( ]*?)>=([0-9a-zA-Z*/.+\\-)( ]*?)\\)( )*<=( )*\\?( )*",
            goal,
        )
        if match:
            return TAIL_BOUND_UPPER, [
                sympify(t) for t in [match.group(1), match.group(2)]
            ]

        match = re.search(
            "^P\\(([0-9a-zA-Z*/.+\\-)( ]*?)>([0-9a-zA-Z*/.+\\-)( ]*?)\\)( )*>=( )*\\?( )*",
            goal,
        )
        if match:
            return TAIL_BOUND_LOWER, [
                sympify(t) for t in [match.group(1), match.group(2)]
            ]

        raise ParseException(f"Unknown goal {goal}")
