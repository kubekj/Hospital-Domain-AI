import uuid
from typing import Tuple
import numpy as np


class CBSAgent:

    def __init__(self, start: Tuple[int, int], goal: Tuple[int, int]):
        self.id = uuid.UUID()
        self.start = np.array(start)
        self.goal = np.array(goal)

    def __hash__(self):
        return int(str(self.start[0]) + str(self.start[1]))

    def __eq__(self, other: 'CBSAgent'):
        return np.array_equal(self.start, other.start) and np.array_equal(self.goal, other.goal)

    def __str__(self):
        return str(self.start.tolist())

    def __repr__(self):
        return self.__str__()

