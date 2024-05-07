from typing import NamedTuple, Tuple
from enum import Enum
import numpy as np

Atom = int #Making it easiet to spot the encoded literal
Pos = NamedTuple('Pos', [('row', int), ('col', int)])
# Pos = tuple[int, int]

class Location:
    all_neighbours: np.ndarray  # Use a 3D numpy array to store neighbour positions.
    walls: np.ndarray

    @staticmethod
    def init_arrays(height: int, width: int):
        Location.walls = np.zeros((height, width), dtype=bool)
        Location.all_neighbours = np.empty((height, width), dtype=object)
        for i in range(height):
            for j in range(width):
                Location.all_neighbours[i, j] = []

    @staticmethod
    def calculate_neighbours():
        height, width = Location.walls.shape
        for row in range(height):
            for col in range(width):
                if not Location.walls[row, col]:
                    possibilities = [
                        (row, col - 1), (row, col + 1),
                        (row - 1, col), (row + 1, col)
                    ]
                    valid_neighbours = []
                    for r, c in possibilities:
                        if 0 <= r < height and 0 <= c < width and not Location.walls[r, c]:
                            valid_neighbours.append(Pos(r, c))
                    Location.all_neighbours[row, col] = valid_neighbours

    @staticmethod
    def get_neighbours(loc: Pos) -> list[Pos]:
        row, col = loc
        return Location.all_neighbours[row, col]

    @staticmethod
    def calculate_all_neighbours(walls: list[list[bool]]):
        Location.init_arrays(len(walls), len(walls[0]))
        Location.walls = np.array(walls, dtype=bool)
        Location.calculate_neighbours()

class AtomType(Enum):
    FREE = 0 # unused
    BOX_AT = 1
    AGENT_AT = 2
    ## Free value for 3
    # NEIGHBOUR = 3
    # LOCATION = 3

def encode_pos(row: int, col: int):
    return (col << 18) | (row << 2)

def encode_atom_pos(atom_type: AtomType, loc: Pos, atom_id: int = 0, extra: int = 0) -> Atom:
    return encode_atom(atom_type, loc.row, loc.col, atom_id, extra)

def encode_atom(atom_type: AtomType, row: int, col: int, atom_id: int = 0, extra: int = 0) -> Atom:
    """
    Encode an atom into a 64-bit integer.
        Extra Data: 26 bits at bits 38-63
        Atom ID:    4 bits at bits 34-37
        Column:     16 bits at bits 18-33
        Row:        16 bits at bits 2-17
        Atom Type:  2 bits at bits 0-1

    :param atom_type: AtomType, the type of the atom.
    :param row: int, the row index.
    :param col: int, the column index.
    :param extra: int, extra data to encode, representing location list index or other metadata.
    :return: int, encoded 64-bit integer representing the atom.
    """
    # (extra << 38) |
    return (atom_id << 34) | (col << 18) | (row << 2) | atom_type.value

def get_atom_type(encoded: int) -> int:
    return encoded & 0x3

def get_atom_location(encoded: int) -> tuple[int, int]:
    row = (encoded >> 2) & 0xFFFF
    col = (encoded >> 18) & 0xFFFF
    return row, col

def get_atom_id(encoded: int) -> int:
    return (encoded >> 34) & 0x0F

def decode_atom(encoded: Atom) -> Tuple[AtomType, int, int, int]:
    atom_type = get_atom_type(encoded)
    row, col = get_atom_location(encoded)
    atom_id = get_atom_id(encoded)
    # extra = (encoded >> 38) & 0x3FFFFFF
    return atom_type, row, col, atom_id#, extra

def atom_repr(encoded: Atom) -> str:
    atom_type, row, col, atom_id = decode_atom(encoded)
    atom_id = atom_id if atom_type == AtomType.AGENT_AT.value else f"'{chr(atom_id+ord('A'))}'"
    return f"{AtomType(atom_type).name}({atom_id}, Loc({row},{col}))"

def eval_neighbour(loc1: Pos, loc2: Pos) -> bool:
    row1, col1 = loc1
    row2, col2 = loc2
    row_diff = abs(row1 - row2)
    col_diff = abs(col1 - col2)
    return row_diff + col_diff == 1 # Both numbers come from abs, otherwise this check would be insufficient.

def eval_free(loc: Pos, literals: set[Atom]):
    x_at_locations = {get_atom_location(lit) for lit in literals} #if get_atom_type(lit) != AtomType.FREE.value # We are currently not using the free type
    return loc not in x_at_locations
    ## try, propaly wont work because of the type agent != box
    # return not literals[encoded]

def atoms_by_type(literals: set[Atom], kind: AtomType) -> dict[int, Pos]:
    kind_value = kind.value
    filtered_literals = filter(lambda x: get_atom_type(x) == kind_value, literals)
    return {get_atom_id(lit): Pos(*get_atom_location(lit)) for lit in filtered_literals}
