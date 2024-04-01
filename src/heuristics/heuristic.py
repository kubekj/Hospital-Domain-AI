from abc import ABCMeta, abstractmethod

from src.domain.atom import AgentAt, BoxAt, Free
from src.domain.state import State

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
        goal_count = 0

        # Count agents not at their goal positions
        for agent, goal_loc in self.agent_goal_positions.items():
            agent_loc = None
            for lit in state.literals:
                if isinstance(lit, AgentAt) and lit.agt == agent:
                    agent_loc = lit.loc
            if agent_loc and agent_loc != goal_loc:
                goal_count += 1

        # Count boxes not at their goal positions
        for box, goal_loc in self.box_goal_positions.items():
            box_loc = None
            for lit in state.literals:
                if isinstance(lit, BoxAt) and lit.box == box:
                    box_loc = lit.loc
            if box_loc and box_loc != goal_loc:
                goal_count += 1

        return goal_count

    @abstractmethod
    def f(self, state: "State") -> "int":
        pass

    @abstractmethod
    def __repr__(self):
        raise NotImplementedError
