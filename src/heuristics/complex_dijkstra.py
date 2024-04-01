from src.domain.atom import Free
from src.domain.state import State
from src.heuristics.heuristic import Heuristic
from src.heuristics.manhattan import HeuristicManhattan
from src.heuristics.simple_dijkstra import HeuristicSimpleDijkstra

NO_CHOKE_POINT = -1


# TODO: Transform code so it utilizes this class
class HeuristicComplexDijkstra(Heuristic):
    def __init__(self, initial_state: "State"):
        super().__init__(initial_state)
        self.create_all_dijkstra_mappings(initial_state)
        self.choke_point_detection = [[None for _ in range(self.num_cols)] for _ in range(self.num_rows)]
        self.choke_point_count = {}
        self.distances_from_agent_goals = {}
        self.distances_from_box_goals = {}
        self.initial_distances_from_box = {}

        break_outer_loop = False
        # print(State.walls)
        for row in range(len(State.walls)):
            for col in range(len(State.walls[0])):
                if not State.walls[row][col]:
                    self.name_choke_points(row, col, 0)
                    break_outer_loop = True
                    break
            if break_outer_loop:
                break

    def h(self, state: 'State') -> 'int':
        total_distance = 0
        if state.recalculateDistanceOfBox is not None:
            (box_row, box_col) = state.boxes_dict[state.recalculateDistanceOfBox]
            self.initial_distances_from_box[state.recalculateDistanceOfBox] = (
                HeuristicSimpleDijkstra.create_mapping(state,
                                                       box_row,
                                                       box_col,
                                                       len(State.walls),
                                                       len(State.walls[0])))
            state.recalculateDistanceOfBox = None
        agents_zip = list(zip(state.agent_rows, state.agent_cols))
        for agent_index, (agent_row, agent_col) in enumerate(agents_zip):
            agent = str(agent_index)
            boxes_not_in_goal = [b for b in State.agent_box_dict[agent_index] if
                                 self.box_goal_positions[b] != state.boxes_dict[b]]
            if len(boxes_not_in_goal):
                close_boxes = self.get_close_boxes(agent_row, agent_col, State.agent_box_dict[agent_index],
                                                   state.boxes)
                if len(close_boxes) == 0:
                    # Distance of the agent to the closest box
                    closest_box = min(boxes_not_in_goal,
                                      key=lambda b: self.initial_distances_from_box[b][agent_row][agent_col])
                    total_distance += self.initial_distances_from_box[closest_box][agent_row][agent_col]

                # Distance of boxes to their goals
                for other_box in [b for b in boxes_not_in_goal]:
                    box_position = state.boxes_dict[other_box]
                    self.total_distance += self.distances_from_box_goals[other_box][box_position[0]][box_position[1]]

                # Extra Goal Counting factor
                for box, (row, col) in self.box_goal_positions.items():
                    if state.boxes[row][col] != box:
                        total_distance += 1

                # COOPERATION COST
                if self.choke_point_detection[agent_row][agent_col] != NO_CHOKE_POINT:
                    for in_agent_index, (in_agent_row, in_agent_col) in enumerate(agents_zip[agent_index + 1:]):
                        if self.choke_point_detection[agent_row][agent_col] == \
                                self.choke_point_detection[in_agent_row][in_agent_col]:
                            # total_distance += 1 # VERSION 1: CONSTANT COOPERATION COST
                            total_distance += HeuristicManhattan.calculate_manhattan_distance((agent_row, agent_col), (
                                in_agent_row, in_agent_col))  # VERSION 2: VARIALBE COOPERATION COST

            else:
                if agent in self.distances_from_agent_goals:
                    total_distance += self.distances_from_agent_goals[agent][agent_row][agent_col]

        return total_distance

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

        if break_outer_loop:
            break

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


def get_close_boxes(row, col, agent_boxes, boxes_map):
    close_boxes = {}

    if len(boxes_map) > row + 1 and boxes_map[row + 1][col] in agent_boxes:
        close_boxes[boxes_map[row + 1][col]] = (row + 1, col)

    if 0 <= row - 1 and boxes_map[row - 1][col] in agent_boxes:
        close_boxes[boxes_map[row - 1][col]] = (row - 1, col)

    if len(boxes_map[row]) > col + 1 and boxes_map[row][col + 1] in agent_boxes:
        close_boxes[boxes_map[row][col + 1]] = (row, col + 1)

    if 0 <= col - 1 and boxes_map[row][col - 1] in agent_boxes:
        close_boxes[boxes_map[row][col - 1]] = (row, col - 1)

    return close_boxes
