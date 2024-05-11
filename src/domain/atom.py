from typing import Tuple
import numpy as np
import src.domain.atom_type as AtomType
from src.domain.domain_types import *
from functools import cache

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
                        (row, col - 1),
                        (row, col + 1),
                        (row - 1, col),
                        (row + 1, col),
                    ]
                    valid_neighbours = []
                    for r, c in possibilities:
                        if (
                            0 <= r < height
                            and 0 <= c < width
                            and not Location.walls[r, c]
                        ):
                            valid_neighbours.append(Pos(r, c))
                    Location.all_neighbours[row, col] = valid_neighbours

    @staticmethod
    def get_neighbours(loc: PosIn) -> list[Pos]:
        row, col = loc
        return Location.all_neighbours[row, col]

    @staticmethod
    def calculate_all_neighbours(walls: list[list[bool]]):
        Location.init_arrays(len(walls), len(walls[0]))
        Location.walls = np.array(walls, dtype=bool)
        Location.calculate_neighbours()


def encode_agent(loc: Tuple[int, int], agt) -> Atom:
    return encode_atom(AtomType.AGENT_AT, loc[0], loc[1], agt)


def encode_box(loc: Tuple[int, int], box: Box) -> Atom:
    return encode_atom(AtomType.BOX_AT, loc[0], loc[1], box[0], box[1])


def encode_atom_pos(
    atom_type: AtomType, loc: Pos, atom_label: int = 0, box_extra_id: int = 0
) -> Atom:
    return encode_atom(atom_type, loc.row, loc.col, atom_label, box_extra_id)

@cache
def encode_atom(
    atom_type: int, row: int, col: int, atom_label: int = 0, box_extra_id: int = 0
) -> Atom:
    """
    Encode an atom into a 64-bit integer.
        Extra Data: 26 bits at bits 50-63
        Atom Type:  2 bits at bits  48-49
        Box_ex ID:  8 bits at bits  40-47
        atom label: 8 bits at bits  32-39
        Column:     16 bits at bits 16-31
        Row:        16 bits at bits 0-15

    :param atom_type: AtomType, the type of the atom.
    :param row: int, the row index.
    :param col: int, the column index.
    :param extra: int, extra data to encode, representing location list index or other metadata.
    :return: int, encoded 64-bit integer representing the atom.
    """
    return (
        (atom_type << 48)
        | (box_extra_id << 40)
        | (atom_label << 32)
        | (col << 16)
        | row
    )

def encode_pos(row: int, col: int):
    return (col << 16) | row

def get_atom_type(encoded: Atom) -> int:
    return encoded >> 48 & 0b11

@cache
def get_atom_location(encoded: Atom) -> tuple[int, int]:
    row = encoded & 0xFFFF
    col = (encoded >> 16) & 0xFFFF
    return row, col

def get_atom_id(encoded: Atom) -> int:
    return (encoded >> 32) & 0xFF


def get_box_extra_id(encoded: Atom) -> int:
    return (encoded >> 40) & 0xFF


def get_box(encoded: Atom) -> Box:
    return get_atom_id(encoded), get_box_extra_id(encoded)

def decode_atom(encoded: Atom) -> Tuple[int, int, int, int]:
    atom_type = get_atom_type(encoded)
    row, col = get_atom_location(encoded)
    atom_id = get_atom_id(encoded)
    # extra = (encoded >> 38) & 0x3FFFFFF
    return atom_type, row, col, atom_id  # , extra


def atom_repr(encoded: Atom) -> str:
    atom_type, row, col, atom_id = decode_atom(encoded)
    atom_id, atom_name = (
        (atom_id, "AGENT_AT")
        if atom_type == AtomType.AGENT_AT
        else (f"'{chr(atom_id+ord('A'))}'", "BOX_AT")
    )
    return f"{atom_name}({atom_id}, Loc({row},{col}))"

@cache
def eval_neighbour(loc1: PosIn, loc2: PosIn) -> bool:
    row1, col1 = loc1
    row2, col2 = loc2
    row_diff = abs(row1 - row2)
    col_diff = abs(col1 - col2)
    return (
        row_diff + col_diff == 1
    )  # Both numbers come from abs, otherwise this check would be insufficient.


def eval_free(loc: PosIn, literals: LiteralList):
    loc_int = encode_pos(*loc)
    x_at_locations = {lit & 0xFFFF_FFFF for lit_type in literals for lit in lit_type}
    return loc_int not in x_at_locations
    ## try, propaly wont work because of the type agent != box
    # return not literals[encoded]

def atoms_by_type(literals: LiteralList, kind: AtomType) -> dict[int, Pos]:
    return {get_atom_id(lit): Pos(*get_atom_location(lit)) for lit in literals[kind]}

def get_box_dict(literals: LiteralList, kind: AtomType) -> dict[Box, Pos]:
    return {get_box(lit): Pos(*get_atom_location(lit)) for lit in literals[kind]}