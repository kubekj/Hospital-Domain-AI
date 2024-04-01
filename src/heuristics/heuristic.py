import math
import heapq

from abc import ABCMeta, abstractmethod
from src.utils.info import Info
from src.domain.atom import AgentAt, BoxAt, Free, Location
from src.domain.state import State
from enum import Enum, unique

NO_CHOKE_POINT = -1

class Heuristic(metaclass=ABCMeta):
    FIRST_ERROR = False

    def __init__(self, initial_state: 'State'):
        self.box_goal_positions = {}
        self.agent_goal_positions = {}
        for lit in initial_state.goal_literals:
            if isinstance(lit, AgentAt):
                self.agent_goal_positions[lit.agt] = lit.loc
            elif isinstance(lit, BoxAt):
                self.box_goal_positions[lit.box] = lit.loc

        self.num_rows = len(Free.walls)
        self.num_cols = len(Free.walls[0])

    def h(self, state: 'State') -> 'int':
        total_distance = 0
        for agent_index, (agent_row, agent_col) in enumerate(zip(state.agent_rows, state.agent_cols)):
            agent_goal = str(agent_index)
            if agent_goal in self.agent_goal_positions:
                goal_row, goal_col = self.agent_goal_positions[agent_goal]
                if agent_row != goal_row or agent_col != goal_col:
                    total_distance += 1

        for box, (row, col) in self.box_goal_positions.items():
            if state.boxes[row][col] != box:
                total_distance += 1

        return total_distance

    @abstractmethod
    def f(self, state: "State") -> "int":
        pass

    @abstractmethod
    def __repr__(self):
        raise NotImplementedError
