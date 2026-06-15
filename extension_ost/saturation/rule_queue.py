import heapq

from typing import List, Set, Tuple

from extension_ost.saturation.saturation_rules.rule import Rule


class RuleQueue:
    heap: List[Tuple[int, int, Rule]] = []

    def __init__(self, rules: List[Rule]):
        self.add_rules(rules)

    def add_rules(self, rules: List[Rule]):
        for rule in rules:
            heapq.heappush(self.heap, [-rule.priority, rule.__hash__(), rule])

    def get_next(self) -> Rule:
        return heapq.heappop(self.heap)[2]
