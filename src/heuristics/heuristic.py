from abc import ABCMeta, abstractmethod

from src.domain.atom import Location, AtomType, atoms_by_type, get_atom_type, Pos, Atom
from src.domain.state import State

# Goal count as a default heuristic
def extract_goal_positions(atom_type: AtomType, initial_state: State) -> dict[Atom, Pos]:
    return atoms_by_type(initial_state.goal_literals, atom_type)


def count_goals_not_met(state: State, goal_positions: dict[Atom, Pos], atom_type: AtomType):
    return sum(1 for item, goal_loc in goal_positions.items()
               if any(get_atom_type(lit) == atom_type and lit.loc != goal_loc
                    for lit in state.literals))


class Heuristic(metaclass=ABCMeta):
    FIRST_ERROR = False

    def __init__(self, initial_state: 'State'):
        self.box_goal_positions = extract_goal_positions(AtomType.BOX_AT, initial_state)
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
