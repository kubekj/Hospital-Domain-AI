from collections import deque

from src.frontiers.frontier import Frontier
from src.domain.state import State


class FrontierDFS(Frontier):
    def __init__(self):
        super().__init__()
        self.stack = deque()
        self.set = set()

    def add(self, state: 'State'):
        self.stack.append(state)
        self.set.add(state)

    def pop(self) -> 'State':
        state = self.stack.pop()
        self.set.remove(state)
        return state

    def is_empty(self) -> 'bool':
        return len(self.stack) == 0

    def size(self) -> 'int':
        return len(self.stack)

    def contains(self, state: 'State') -> 'bool':
        return state in self.set

    def get_name(self):
        return 'Depth-first search'
