from typing import List, Tuple

from termination.util.enums import LogicalState, TerminationProperty


class SMTFormula:
    def __init__(
        self, formula: str, implications: List[Tuple[LogicalState, TerminationProperty]]
    ) -> None:
        self.formula = formula
        self.implications = implications

    def __str__(self) -> str:
        return (
            "The following implications hold:\n"
            + "\n".join(
                [f"{str(ls).ljust(15)}=>    {rs}" for ls, rs in self.implications]
            )
            + f"for the following formula: \n\n{self.formula}"
        )
