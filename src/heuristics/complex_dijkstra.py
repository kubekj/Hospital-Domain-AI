from src.domain.atom import Free
from src.domain.state import State
from src.heuristics.heuristic import Heuristic
from src.heuristics.simple_dijkstra import HeuristicSimpleDijkstra

NO_CHOKE_POINT = -1


# TODO: Transform code so it utilizes this class
class HeuristicComplexDijkstra(Heuristic):
    def __init__(self, initial_state: "State", num_rows, num_cols):
        super().__init__(initial_state)
        self.create_all_dijkstra_mappings(initial_state)
        self.choke_point_detection = [[None for _ in range(num_cols)] for _ in range(num_rows)]
        self.choke_point_count = {}

    def f(self, state: 'State') -> 'int':
        return self.h(state)

    def __repr__(self):
        return "Dijkstra heuristic"

    def name_choke_points(self, row, col, id):
        if State.walls[row][col]:
            print("ERROR: Started name_choke_points in a wall.")
            return
        possible_moves = []
        if len(State.walls) > row + 1 and not State.walls[row + 1][col]:
            possible_moves += [(row + 1, col)]

        if 0 <= row - 1 and not State.walls[row - 1][col]:
            possible_moves += [(row - 1, col)]

        if len(State.walls[row]) > col + 1 and not State.walls[row][col + 1]:
            possible_moves += [(row, col + 1)]

        if 0 <= col - 1 and not State.walls[row][col - 1]:
            possible_moves += [(row, col - 1)]
        if len(possible_moves) > 2:
            self.choke_point_detection[row][col] = NO_CHOKE_POINT
        else:
            self.choke_point_detection[row][col] = id
            if not id in self.choke_point_count:
                self.choke_point_count[id] = 0
            self.choke_point_count[id] += 1

        for move in possible_moves:
            if self.choke_point_detection[move[0]][move[1]] is None:
                if self.choke_point_detection[row][col] == NO_CHOKE_POINT:
                    id += 1
                self.name_choke_points(move[0], move[1], id)

    break_outer_loop = False
    # print(State.walls)
    for row in range(len(State.walls)):
        for col in range(len(State.walls[0])):
            if not State.walls[row][col]:
                name_choke_points(row, col, 0)
                break_outer_loop = True
                break

        if break_outer_loop: break

    def create_all_dijkstra_mappings(self, state):
        num_rows = len(Free.walls)
        num_cols = len(Free.walls[0])
        self.distances_from_agent_goals = {}
        self.distances_from_box_goals = {}
        self.initial_distances_from_box = {}
        for agent, loc in self.agent_goal_positions.items():
            self.distances_from_agent_goals[agent] = HeuristicSimpleDijkstra.create_mapping(state, loc.row, loc.col,
                                                                                            num_rows, num_cols)
        for box, loc in self.box_goal_positions.items():
            self.distances_from_box_goals[box] = HeuristicSimpleDijkstra.create_mapping(state, loc.row, loc.col,
                                                                                        num_rows, num_cols)
        for box, loc in state.boxes_dict.items():
            self.initial_distances_from_box[box] = HeuristicSimpleDijkstra.create_mapping(state, loc.row, loc.col,
                                                                                          num_rows, num_cols)
