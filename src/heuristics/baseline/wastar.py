from src.heuristics.heuristic import Heuristic
from src.domain.state import State


class HeuristicWeightedAStar(Heuristic):
    def __init__(self, initial_state: "State", w: "int"):
        super().__init__(initial_state)
        self.w = w

    def f(self, state: 'State') -> 'int':
        return state.g + self.w * self.h(state)

    def __repr__(self):
        return 'WA*({}) evaluation'.format(self.w)
