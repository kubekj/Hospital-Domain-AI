from abc import ABCMeta, abstractmethod

from src.domain.atom import AgentAt, BoxAt, Free
from src.domain.state import State

# Goal count as a default heuristic
def extract_goal_positions(atom_type, initial_state, item_attr):
    return {getattr(lit, item_attr): lit.loc for lit in initial_state.goal_literals if isinstance(lit, atom_type)}


def count_goals_not_met(state, goal_positions, atom_type, item_attr):
    return sum(1 for item, goal_loc in goal_positions.items()
               if any(isinstance(lit, atom_type)
                      and getattr(lit, item_attr) == item
                      and lit.loc != goal_loc for lit in state.literals))
#

class Heuristic(metaclass=ABCMeta):
    FIRST_ERROR = False

    def __init__(self, initial_state: 'State'):
        self.box_goal_positions = extract_goal_positions(BoxAt, initial_state, 'box')
        self.agent_goal_positions = extract_goal_positions(AgentAt, initial_state, 'agt')
        self.num_rows = len(Free.walls)
        self.num_cols = len(Free.walls[0])

    def h(self, state: 'State') -> 'int':
        return count_goals_not_met(state, self.agent_goal_positions, AgentAt, 'agt') + \
            count_goals_not_met(state, self.box_goal_positions, BoxAt, 'box')

    @abstractmethod
    def f(self, state: "State") -> "int":
        pass

    @abstractmethod
    def __repr__(self):
        raise NotImplementedError
