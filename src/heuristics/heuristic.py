import math
import heapq

from abc import ABCMeta, abstractmethod
from src.utils.info import Info
from src.domain.atom import AgentAt, BoxAt, Free, Location
from src.domain.state import State
from enum import Enum, unique

@unique
class HeuristicType(Enum):
    Simple = 0,
    SimpleDijkstra = 1,
    ComplexDijkstra = 2
    Manhattan = 3


NO_CHOKEPOINT = -1


class Heuristic(metaclass=ABCMeta):
    strategy: HeuristicType = HeuristicType.Simple
    FIRST_ERROR = False

    def __init__(self, initial_state: 'State'):
        self.box_goal_positions = {}
        self.agent_goal_positions = {}
        for lit in State.goal_literals:
            if isinstance(lit, AgentAt):
                self.agent_goal_positions[lit.agt] = lit.loc
            elif isinstance(lit, BoxAt):
                self.box_goal_positions[lit.box] = lit.loc

        num_rows = len(Free.walls)
        num_cols = len(Free.walls[0])
        # TODO: Move the logic to Dijkstra Heuristic class
        match Heuristic.strategy:
            case HeuristicType.SimpleDijkstra:
                self.distances_from_agent_goals = {}
                self.distances_from_box_goals = {}
                self.initial_distances_from_box = {}
                for agent, loc in self.agent_goal_positions.items():
                    self.distances_from_agent_goals[agent] = create_dijsktra_mapping(
                        initial_state, loc.row, loc.col, num_rows, num_cols
                    )
            case HeuristicType.ComplexDijkstra:
                self.create_all_dijkstra_mappings(initial_state)
                self.choke_point_detection = [[None for _ in range(num_cols)] for _ in range(num_rows)]
                self.choke_point_count = {}

                def name_chokepoints(row, col, id):
                    if State.walls[row][col]:
                        print("ERROR: Started name_chokepoints in a wall.")
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
                        self.choke_point_detection[row][col] = NO_CHOKEPOINT
                    else:
                        self.choke_point_detection[row][col] = id
                        if not id in self.choke_point_count:
                            self.choke_point_count[id] = 0
                        self.choke_point_count[id] += 1

                    for move in possible_moves:
                        if self.choke_point_detection[move[0]][move[1]] is None:
                            if self.choke_point_detection[row][col] == NO_CHOKEPOINT:
                                id += 1
                            name_chokepoints(move[0], move[1], id)

                break_outter_loop = False
                # print(State.walls)
                for row in range(len(State.walls)):
                    for col in range(len(State.walls[0])):
                        if not State.walls[row][col]:
                            name_chokepoints(row, col, 0)
                            break_outter_loop = True
                            break
                    if break_outter_loop: break
                # for row in range(len(State.walls)):
                # print(State.walls[row])
                # print(self.chokepoint_detection[row])

            case _:
                pass

    def h(self, state: 'State') -> 'int':
        total_distance = 0
        # if len(state.boxes_dict) != sum([len(v) for b,v in State.agent_box_dict.items()]):
        #     return math.inf
        # TODO: Modularize the code so it's more readable - move these to separate functions inside to specific classes
        match Heuristic.strategy:
            case HeuristicType.Simple:
                for agent_index, (agent_row, agent_col) in enumerate(
                        zip(state.agent_rows, state.agent_cols)
                ):
                    agent_goal = str(agent_index)
                    if agent_goal in self.agent_goal_positions:
                        goal_row, goal_col = self.agent_goal_positions[agent_goal]
                        if agent_row != goal_row or agent_col != goal_col:
                            total_distance += 1

                for box, (row, col) in self.box_goal_positions.items():
                    if state.boxes[row][col] != box:
                        total_distance += 1
            case HeuristicType.SimpleDijkstra:
                for agent_index, agent_loc in state.agent_locations.items():
                    # agent = str(agent_index)
                    agent = agent_index
                    try:
                        if agent in self.distances_from_agent_goals:
                            total_distance += self.distances_from_agent_goals[agent][agent_loc.row][agent_loc.col]
                    except Exception as ex:
                        print(Info.level_name)
                        print(ex)
                        print(self.distances_from_agent_goals)
                        break
            case HeuristicType.ComplexDijkstra:
                # In state.result if an agent moves away from a box that has been previously moved
                if state.recalculateDistanceOfBox is not None:
                    (box_row, box_col) = state.boxes_dict[state.recalculateDistanceOfBox]
                    self.initial_distances_from_box[state.recalculateDistanceOfBox] = create_dijsktra_mapping(state, box_row, box_col, len(State.walls), len(State.walls[0]))
                    state.recalculateDistanceOfBox = None
                agents_zip = list(zip(state.agent_rows, state.agent_cols))
                for agent_index, (agent_row, agent_col) in enumerate(agents_zip):
                    agent = str(agent_index)
                    boxes_not_in_goal = [b for b in State.agent_box_dict[agent_index] if
                                         self.box_goal_positions[b] != state.boxes_dict[b]]
                    if len(boxes_not_in_goal):
                        close_boxes = get_close_boxes(agent_row, agent_col, State.agent_box_dict[agent_index],
                                                      state.boxes)
                        if len(close_boxes) == 0:
                            # Distance of the agent to the closest box
                            closest_box = min(boxes_not_in_goal,
                                              key=lambda b: self.initial_distances_from_box[b][agent_row][agent_col])
                            total_distance += self.initial_distances_from_box[closest_box][agent_row][agent_col]

                        # Distance of boxes to their goals
                        for other_box in [b for b in boxes_not_in_goal]:
                            box_position = state.boxes_dict[other_box]
                            total_distance += self.distances_from_box_goals[other_box][box_position[0]][box_position[1]]

                        # Extra Goal Counting factor
                        for box, (row, col) in self.box_goal_positions.items():
                            if state.boxes[row][col] != box:
                                total_distance += 1

                        # COOPERATION COST
                        if self.choke_point_detection[agent_row][agent_col] != NO_CHOKEPOINT:
                            for in_agent_index, (in_agent_row, in_agent_col) in enumerate(agents_zip[agent_index + 1:]):
                                if self.choke_point_detection[agent_row][agent_col] == \
                                        self.choke_point_detection[in_agent_row][in_agent_col]:
                                    # total_distance += 1 # VERSION 1: CONSTANT COOPERATION COST
                                    total_distance += calculate_manhattan_distance((agent_row, agent_col), (
                                        in_agent_row, in_agent_col))  # VERSION 2: VARIALBE COOPERATION COST

                    else:
                        if agent in self.distances_from_agent_goals:
                            total_distance += self.distances_from_agent_goals[agent][agent_row][agent_col]

                    # Here we need to calculate the following:
                    # If the agent has any box of the same color that's not in their goal :
                    #   If not box close:
                    #       - Go to the closest box: Distance from the agent to the closest box
                    #
                    #   - Take the box with the closest goal to that goal: Distance from the closest box goal
                    # Else:
                    #   If it has a agent goal:
                    #       - Go to the closest agent goal: Distance from the agent goal

            case HeuristicType.Manhattan:
                # Calculate distance from boxes to their goals
                for box_row in range(len(state.boxes)):
                    for box_col in range(len(state.boxes[box_row])):
                        box = state.boxes[box_row][box_col]
                        if box:  # If there's a box at this position
                            for goal, (goal_row, goal_col) in self.box_goal_positions.items():
                                if box == goal:
                                    distance = calculate_manhattan_distance((box_row, box_col), (goal_row, goal_col))
                                    total_distance += distance
                                    break
                # Calculate distance from agents to their goals
                for agent_index, (agent_row, agent_col) in enumerate(zip(state.agent_rows, state.agent_cols)):
                    agent_goal = str(agent_index)  # Goals are indexed by their integer representation
                    if agent_goal in self.agent_goal_positions:
                        goal_row, goal_col = self.agent_goal_positions[agent_goal]
                        distance = calculate_manhattan_distance((agent_row, agent_col), (goal_row, goal_col))
                    else:
                        min_distance = float('inf')  # Start with infinity to ensure any real distance is smaller
                        for goal_ident, (goal_row, goal_col) in self.agent_goal_positions.items():
                            if goal_ident != agent_goal:  # Ensure we're looking at other agents' goals
                                distance = calculate_manhattan_distance((agent_row, agent_col), (goal_row, goal_col))
                                min_distance = min(min_distance, distance)
                        distance = -min_distance  # Use negative distance to encourage moving away
                    total_distance += distance
            case _:
                pass
        # print(total_distance)
        return total_distance

    @abstractmethod
    def f(self, state: "State") -> "int":
        pass

    @abstractmethod
    def __repr__(self):
        raise NotImplementedError

    def create_all_dijkstra_mappings(self, state):
        num_rows = len(Free.walls)
        num_cols = len(Free.walls[0])
        self.distances_from_agent_goals = {}
        self.distances_from_box_goals = {}
        self.initial_distances_from_box = {}
        for agent, loc in self.agent_goal_positions.items():
            self.distances_from_agent_goals[agent] = create_dijsktra_mapping(state, loc.row, loc.col, num_rows, num_cols)
        for box, loc in self.box_goal_positions.items():
            self.distances_from_box_goals[box] = create_dijsktra_mapping(state, loc.row, loc.col, num_rows, num_cols)
        for box, loc in state.boxes_dict.items():
            self.initial_distances_from_box[box] = create_dijsktra_mapping(state, loc.row, loc.col, num_rows, num_cols)

def create_dijsktra_mapping(state: State, row, col, num_rows, num_cols, take_boxes_into_account=False):
    '''Return a map of the shape [num_rows, num_cols] with every cell filled with the distance to the cell (row, col),
    calculated with the Dijkstra algorithm. If a cell (i,j) is a wall, which we know by State.walls[i][j] == true, then
     the distance will be math.inf '''
    distances = [[math.inf for _ in range(num_cols)] for _ in range(num_rows)]

    def my_is_free(row, col):
        if take_boxes_into_account:
            return Free(Location(row, col)).eval(state.literals)
        else:
            return Free.walls[row][col]

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
                new_distance = current_distance + 1  # Distance to adjacent cells is always 1 more
                if new_distance < distances[next_row][next_col]:
                    distances[next_row][next_col] = new_distance
                    heapq.heappush(queue, (new_distance, (next_row, next_col)))

    return distances

def calculate_manhattan_distance(first_position, second_position):
    return abs(first_position[0] - second_position[0]) + abs(first_position[1] - second_position[1])

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
