import heapq
import math

from src.domain.atom import Location, eval_free
from src.heuristics.heuristic import Heuristic
from src.domain.state import State
from src.utils.info import Info


# TODO: Transform code so it utilizes this class
class HeuristicSimpleDijkstra(Heuristic):
    def __init__(self, initial_state: "State"):
        super().__init__(initial_state)
        self.distances_from_agent_goals = {}
        self.distances_from_box_goals = {}
        self.initial_distances_from_box = {}
        for agent, loc in self.agent_goal_positions.items():
            self.distances_from_agent_goals[agent] = self.create_mapping(
                initial_state, loc.row, loc.col, self.num_rows, self.num_cols
            )

    def h(self, state: "State") -> "int":
        total_distance = 0
        for agent_index, agent_loc in state.agent_locations.items():
            agent = agent_index
            try:
                if agent in self.distances_from_agent_goals:
                    total_distance += self.distances_from_agent_goals[agent][
                        agent_loc.row
                    ][agent_loc.col]
            except Exception as ex:
                print('#', Info.level_name)
                print('#', ex)
                # print('#', self.distances_from_agent_goals)
                break
        return total_distance

    def f(self, state: "State") -> "int":
        return self.h(state)

    def __repr__(self):
        return "Dijkstra heuristic"

    @staticmethod
    def create_mapping(
        state: State, row, col, num_rows, num_cols, take_boxes_into_account=False
    ) -> list[list[int | float]]:
        """
        Return a map of the shape [num_rows, num_cols] with every cell filled with the distance to the cell (row, col),
        calculated with the Dijkstra algorithm. If a cell (i,j) is a wall, which we know by State.walls[i][j] == true, then
        the distance will be math.inf
        """
        distances: list[list[int | float]] = [
            [math.inf] * num_cols for _ in range(num_rows)
        ]

        def my_is_free(row, col):
            if take_boxes_into_account:
                return eval_free(
                    Location.all_locations(row, col), state.literals
                )  # FIXME Broke?
            else:
                return Location.walls[row][col]

        # Check if the initial position is a wall
        if my_is_free(row, col):
            return distances  # If the starting cell is a wall, return the distances as initialized

        distances[row][col] = 0  # Distance to itself is 0

        # Priority queue: (distance, (row, col))
        queue = [(0, (row, col))]

        # Directions for up, down, left, right movements
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        while queue:
            current_distance, (current_row, current_col) = heapq.heappop(queue)

            for d_row, d_col in directions:
                next_row, next_col = current_row + d_row, current_col + d_col

                # Check boundaries and walls
                if (
                    0 <= next_row < num_rows
                    and 0 <= next_col < num_cols
                    and not my_is_free(next_row, next_col)
                ):
                    new_distance = (
                        current_distance + 1
                    )  # Distance to adjacent cells is always 1 more
                    if new_distance < distances[next_row][next_col]:
                        distances[next_row][next_col] = new_distance
                        heapq.heappush(queue, (new_distance, (next_row, next_col)))

        return distances
