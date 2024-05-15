import numpy as np
from src.domain.domain_types import *

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
        return list[Pos](Location.all_neighbours[row, col])

    @staticmethod
    def calculate_all_neighbours(walls: list[list[bool]]):
        Location.init_arrays(len(walls), len(walls[0]))
        Location.walls = np.array(walls, dtype=bool)
        Location.calculate_neighbours()