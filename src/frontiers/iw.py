from itertools import chain, combinations

from src.frontiers.baseline.best_first import FrontierBestFirst
from src.heuristics.heuristic import Heuristic
from src.domain.state import State


class FrontierIW(FrontierBestFirst):
    def __init__(self, heuristic: "Heuristic", width=1):
        super().__init__(heuristic)
        self.width = width
        self.known_combinations = set()
        print(f"#Initialized frontier with width {self.width}")

    def add(self, state: "State"):
        if self.is_novel_combination(state.literals):
            super().add(state)

    def pop(self) -> "State":
        return super().pop()

    def is_empty(self) -> "bool":
        return super().is_empty()

    def size(self) -> "int":
        return super().size()

    def contains(self, state: "State") -> "bool":
        return super().contains(state)

    def get_name(self):
        return "Iterated-width search"

    def is_novel_combination(self, elements):
        """
        Check if there's a new combination of elements of size self.width.

        :param elements: A set of elements to check for novelty.
        :return: True if there's a novel combination, False otherwise.
        """
        seen = self.known_combinations
        new_combinations = set()

        # Generate all combinations of size self.width from the elements
        for comb in combinations(chain(*elements), self.width):
            froz_comb = frozenset(comb)
            if froz_comb not in seen:
                new_combinations.add(froz_comb)
        
        # If there is any novel combination, return True and update the set
        if new_combinations:
            self.known_combinations.update(new_combinations)
            return True

        return False
