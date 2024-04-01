import heapq
import itertools

from src.frontiers.frontier import Frontier
from src.heuristics.heuristic import Heuristic
from src.domain.state import State


class FrontierBestFirst(Frontier):
    def __init__(self, heuristic: "Heuristic"):
        super().__init__()
        self.heuristic = heuristic
        self.pqueue = []
        self.set = set()
        self.counter = itertools.count()

    def add(self, state: 'State'):
        priority = self.heuristic.f(state)
        # state_id is added to solve queue priority conflicts
        # (if they are the same, it takes the one with smaller id first)
        state_id = next(self.counter)
        heapq.heappush(self.pqueue, (priority, state_id, state))
        self.set.add(state)

    def pop(self) -> 'State':
        _, _, state = heapq.heappop(self.pqueue)
        self.set.remove(state)
        return state

    def is_empty(self) -> 'bool':
        return len(self.pqueue) == 0

    def size(self) -> 'int':
        return len(self.pqueue)

    def contains(self, state: 'State') -> 'bool':
        return state in self.set

    def get_name(self):
        return "Best-first search using {}".format(self.heuristic)
