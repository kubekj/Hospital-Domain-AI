import heapq
import itertools
from abc import ABCMeta, abstractmethod
from collections import deque
from heuristic import Heuristic
from itertools import combinations


class Frontier(metaclass=ABCMeta):
    @abstractmethod
    def add(self, state: 'State'): raise NotImplementedError

    @abstractmethod
    def pop(self) -> 'State': raise NotImplementedError

    @abstractmethod
    def is_empty(self) -> 'bool': raise NotImplementedError

    @abstractmethod
    def size(self) -> 'int': raise NotImplementedError

    @abstractmethod
    def contains(self, state: 'State') -> 'bool': raise NotImplementedError

    @abstractmethod
    def get_name(self): raise NotImplementedError


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
        return 'breadth-first search'


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
        return 'depth-first search'


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
        return "best-first search using {}".format(self.heuristic)


class FrontierIW(FrontierBestFirst):
    def __init__(self, heuristic: "Heuristic", width = 1):
        super().__init__(heuristic)
        self.width = width
        self.known_combinations = set()
        print(f"Initialized frontier with width {self.width}")

    def add(self, state: 'State'):
        if self.is_novel_combination(state.literals):
            super().add(state)

    def pop(self) -> 'State':
        return super().pop()

    def is_empty(self) -> 'bool':
        return super().is_empty()

    def size(self) -> 'int':
        return super().size()

    def contains(self, state: 'State') -> 'bool':
        return super().contains(state)

    def get_name(self):
        return 'iterated-width search'
    
    def is_novel_combination(self, elements):
        """
        Check if there's a new combination of elements of size i.
        
        :param elements: A set of elements to check for novelty.
        :param i: The size of the combinations to check.
        :return: True if there's a novel combination, False otherwise.
        """

        # Generate all combinations of size i from the elements
        new_combinations = set(combinations(elements, self.width))

        # Check if there's any combination that we have not seen before
        novel = not new_combinations.issubset(self.known_combinations)

        # If there is a novel combination, add it to the set of known combinations
        if novel:
            self.known_combinations.update(new_combinations)

        return novel