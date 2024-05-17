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
        Check if there's a new combination of elements of size i.

        :param elements: A set of elements to check for novelty.
        :param i: The size of the combinations to check.
        :return: True if there's a novel combination, False otherwise.
        """
        # Generate all combinations of size i from the elements
        new_combinations = set(frozenset(comb) for comb in combinations(chain(*elements), self.width))

        # Check if there's any combination that we have not seen before
        novel = not new_combinations.issubset(self.known_combinations)

        # If there is a novel combination, add it to the set of known combinations
        if novel:
            self.known_combinations.update(new_combinations)

        return novel
