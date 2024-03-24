from collections import deque

from src.frontiers.frontier import Frontier
from src.domain.state import State


class FrontierBFS(Frontier):
    def __init__(self):
        super().__init__()
        self.queue = deque()
        self.set = set()

    def add(self, state: 'State'):
        self.queue.append(state)
        self.set.add(state)

    def pop(self) -> 'State':
        state = self.queue.popleft()
        self.set.remove(state)
        return state

    def is_empty(self) -> 'bool':
        return len(self.queue) == 0

    def size(self) -> 'int':
        return len(self.queue)

    def contains(self, state: 'State') -> 'bool':
        return state in self.set

    def get_name(self):
        return 'Breadth-first search'
