import uuid
from typing import Tuple, Set
import numpy as np

from src.cbs.cbsbox import CBSBox


class CBSAgent:

    def __init__(self, agent_id: int, start: Tuple[int, int], goal: Tuple[int, int], boxes: Set['CBSBox']):
        self.id = agent_id
        self.position = np.array(start, dtype=int)
        self.goal = np.array(goal, dtype=int)
        self.boxes = boxes

    def move(self, delta_row: int, delta_col: int):
        self.position += np.array([delta_row, delta_col])

    def is_at_goal(self):
        return np.array_equal(self.position, self.goal)

    def __hash__(self):
        return int(str(self.position[0]) + str(self.position[1]))

    def __eq__(self, other: 'CBSAgent'):
        return np.array_equal(self.position, other.position) and np.array_equal(self.goal, other.goal)

    def __str__(self):
        return str(self.position.tolist())

    def __repr__(self):
        return self.__str__()

