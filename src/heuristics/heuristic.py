from abc import ABCMeta, abstractmethod

from src.domain.location import Location
from src.domain.atom import Box, AtomType, atoms_by_type, Pos, Atom, get_box_dict
from src.domain.state import State

# Goal count as a default heuristic
def extract_goal_positions(atom_type: AtomType, initial_state: State) -> dict[int, Pos]:
    return atoms_by_type(initial_state.goal_literals, atom_type)


def count_goals_not_met(state: State, goal_positions: dict[Atom, Pos], atom_type: AtomType):
    return sum(1 for item, goal_loc in goal_positions.items()
               if any(lit.loc != goal_loc for lit in state.literals[atom_type]))


class Heuristic(metaclass=ABCMeta):
    FIRST_ERROR = False

    def __init__(self, initial_state: 'State'):
        self.box_goal_positions: dict[Box, Pos] = get_box_dict(initial_state.goal_literals, AtomType.BOX_AT)
        self.agent_goal_positions = extract_goal_positions(AtomType.AGENT_AT, initial_state)
        self.num_rows = len(Location.walls)
        self.num_cols = len(Location.walls[0])

    def h(self, state: 'State') -> 'int':
        return count_goals_not_met(state, self.agent_goal_positions, AtomType.AGENT_AT) + \
            count_goals_not_met(state, self.box_goal_positions, AtomType.BOX_AT)

    @abstractmethod
    def f(self, state: "State") -> "int|float":
        pass

    @abstractmethod
    def __repr__(self):
        raise NotImplementedError
