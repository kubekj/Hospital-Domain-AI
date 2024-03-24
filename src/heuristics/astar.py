from src.heuristics.heuristic import Heuristic
from src.domain.state import State


class HeuristicAStar(Heuristic):
    def __init__(self, initial_state: "State"):
        super().__init__(initial_state)

    def f(self, state: 'State') -> 'int':
        return state.g + self.h(state)

    def __repr__(self):
        return 'A* evaluation'
