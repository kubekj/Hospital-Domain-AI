from src.domain.atom import Location, AtomType, atoms_by_type
from src.domain.state import State
from src.heuristics.heuristic import Heuristic
from src.heuristics.manhattan import HeuristicManhattan
from src.heuristics.simple_dijkstra import HeuristicSimpleDijkstra

NO_CHOKE_POINT = -1


# TODO: Transform code so it utilizes this class
class HeuristicComplexDijkstra(Heuristic):
    def __init__(self, initial_state: State):
        super().__init__(initial_state)
        self.create_all_dijkstra_mappings(initial_state)
        self.choke_point_detection = [[None] * self.num_cols for _ in range(self.num_rows)]
        self.choke_point_count = {}

        break_outer_loop = False
        # print(Location.walls)
        for row in range(len(Location.walls)):
            for col in range(len(Location.walls[0])):
                if not Location.walls[row][col]:
                    self.name_choke_points(row, col, 0)
                    break_outer_loop = True
                    break
            if break_outer_loop:
                break

    def h(self, state: State) -> int:
        total_distance = 0
        agents = atoms_by_type(state.literals, AtomType.AGENT_AT)
        boxes = atoms_by_type(state.literals, AtomType.BOX_AT)

        for agt, box in enumerate(state.recalculateDistanceOfBox):
            if box != None:
                # print(f"Recalculating box {box} last moved by agent {agt}")
                self.initial_distances_from_box[box] = (
                    HeuristicSimpleDijkstra.create_mapping(state,
                                                        boxes[box].row,
                                                        boxes[box].col,
                                                        len(Location.walls),
                                                        len(Location.walls[0])))

        for agent, agent_loc in agents.items():
            try:
                boxes_not_in_goal = [b for b in State.agent_box_dict[agent] if
                                     b in self.box_goal_positions and
                                        self.box_goal_positions[b] != boxes[b]]
            except Exception as exc:
                print(State.agent_box_dict)
                print(self.box_goal_positions)
                print('H' in self.box_goal_positions)
                raise Exception(exc)

            if len(boxes_not_in_goal):
                close_boxes = get_close_boxes(agent_loc, {b: boxes[b] for b in boxes if b in State.agent_box_dict[agent]})
                if len(close_boxes) == 0:
                    # Distance of the agent to the closest box
                    closest_box = min(boxes_not_in_goal,
                                      key=lambda b: self.initial_distances_from_box[b][agent_loc.row][agent_loc.col])
                    total_distance += self.initial_distances_from_box[closest_box][agent_loc.row][agent_loc.col]

                # Distance of boxes to their goals
                for other_box in boxes_not_in_goal:
                    box_position = boxes[other_box]
                    total_distance += self.distances_from_box_goals[other_box][box_position.row][box_position.col]

                # Extra Goal Counting factor
                for box, box_loc in self.box_goal_positions.items():
                    if boxes[box] != box_loc:
                        total_distance += 1

                # COOPERATION COST
                # if self.choke_point_detection[agent_loc.row][agent_loc.col] != NO_CHOKE_POINT:
                #     for in_agent_index, (in_agent_row, in_agent_col) in enumerate(agents[agent_index + 1:]):
                #         if self.choke_point_detection[agent_loc.row][agent_loc.col] == \
                #                 self.choke_point_detection[in_agent_row][in_agent_col]:
                #             # total_distance += 1 # VERSION 1: CONSTANT COOPERATION COST
                #             total_distance += HeuristicManhattan.calculate_manhattan_distance((agent_loc.row, agent_loc.col), (
                #                 in_agent_row, in_agent_col))  # VERSION 2: VARIALBE COOPERATION COST

            else:
                if agent in self.distances_from_agent_goals:
                    total_distance += self.distances_from_agent_goals[agent][agent_loc.row][agent_loc.col]

        return total_distance

    def f(self, state: State) -> int:
        return self.h(state)

    def __repr__(self):
        return "Dijkstra heuristic"

    def name_choke_points(self, row, col, id):
        if Location.walls[row][col]:
            print("ERROR: Started name_choke_points in a wall.")
            return
        possible_moves = []
        if len(Location.walls) > row + 1 and not Location.walls[row + 1][col]:
            possible_moves += [(row + 1, col)]

        if 0 <= row - 1 and not Location.walls[row - 1][col]:
            possible_moves += [(row - 1, col)]

        if len(Location.walls[row]) > col + 1 and not Location.walls[row][col + 1]:
            possible_moves += [(row, col + 1)]

        if 0 <= col - 1 and not Location.walls[row][col - 1]:
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

    def create_all_dijkstra_mappings(self, state: State):
        num_rows = len(Location.walls)
        num_cols = len(Location.walls[0])
        self.distances_from_agent_goals = {}
        self.distances_from_box_goals = {}
        self.initial_distances_from_box = {}
        for agent, loc in self.agent_goal_positions.items():
            self.distances_from_agent_goals[agent] = HeuristicSimpleDijkstra.create_mapping(state, loc.row, loc.col,
                                                                                            num_rows, num_cols)
        for box, loc in self.box_goal_positions.items():
            self.distances_from_box_goals[box] = HeuristicSimpleDijkstra.create_mapping(state, loc.row, loc.col,
                                                                                        num_rows, num_cols)
            
        boxes = atoms_by_type(state.literals, AtomType.BOX_AT)
        for box, loc in boxes.items():
            self.initial_distances_from_box[box] = HeuristicSimpleDijkstra.create_mapping(state, loc.row, loc.col,
                                                                                          num_rows, num_cols)


def get_close_boxes(loc: Location, boxes: dict):
    close_boxes = {}

    for neig in loc.neighbours:
        for box, box_loc in boxes.items():
            if box_loc == neig:
                close_boxes[box] = neig

    return close_boxes
