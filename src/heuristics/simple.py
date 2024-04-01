from src.domain.state import State
from src.heuristics.heuristic import Heuristic


class HeuristicSimple(Heuristic):
    def __init__(self, initial_state: 'State'):
        super().__init__(initial_state)

    def f(self, state):
        return self.h(state)

    def __repr__(self):
        return "Simple heuristic"
