from typing import Tuple
from src.domain.atom import Atom, Box, Location, AtomType, Pos, atoms_by_type
from src.domain.state import State
from src.heuristics.heuristic import Heuristic
from src.heuristics.manhattan import HeuristicManhattan
from src.heuristics.simple_dijkstra import HeuristicSimpleDijkstra

NO_CHOKE_POINT = -1


class HeuristicComplexDijkstra(Heuristic):
    def __init__(self, initial_state: State):
        super().__init__(initial_state)
        self.distances = None
        self.create_all_dijkstra_mappings(initial_state)
        self.choke_point_detection = [
            [None] * self.num_cols for _ in range(self.num_rows)
        ]
        self.choke_point_count = {}
        self.setup_choke_points()
        self.agent_assigned_to_box = self.assign_boxes_to_agents(initial_state)
        self.box_goal_assigned_to_box = self.assign_boxes_to_goals(initial_state)
        self.box_priority = self.calculate_box_priority(initial_state)

    def setup_choke_points(self):
        for row, row_walls in enumerate(Location.walls):
            for col, is_wall in enumerate(row_walls):
                if not is_wall:
                    self.name_choke_points(row, col, 0)
                    return

    def calculate_box_priority(self, initial_state):
        box_priority = {}
        for agent, agent_boxes in self.agent_assigned_to_box.items():
            agent_loc = initial_state.agent_locations[agent]
            sorted_boxes = sorted(
                agent_boxes,
                key=lambda b: self.distances[initial_state.box_locations[b]][
                    agent_loc.row
                ][agent_loc.col],
            )
            box_priority[agent] = {
                box: get_priority(i) for i, box in enumerate(sorted_boxes)
            }
        return box_priority

    def h(self, state: State) -> float | int:
        total_distance = 0

        for agent, box in enumerate(state.recalculateDistanceOfBox):
            if box is not None:
                self.get_distances(state, state.box_locations[box])
                state.recalculateDistanceOfBox[agent] = None

        for agent, agent_loc in state.agent_locations.items():
            boxes_not_in_goal = self.get_boxes_not_in_goal(agent, state)
            total_distance += self.calculate_total_distance(
                agent, agent_loc, boxes_not_in_goal, state
            )

        return total_distance

    def get_boxes_not_in_goal(self, agent, state):
        return [
            b
            for b_name in State.agent_box_dict[agent]
            for b in State.boxes[b_name]
            if b in self.box_goal_positions
            and self.box_goal_positions[self.box_goal_assigned_to_box[b]]
            != state.box_locations[b]
        ]

    def calculate_total_distance(self, agent, agent_loc, boxes_not_in_goal, state):
        total_distance = 0
        for box in self.agent_assigned_to_box[agent]:
            if box in self.box_goal_assigned_to_box and box in boxes_not_in_goal:
                box_loc = state.box_locations[box]
                box_distance = self.calculate_box_distance(
                    agent_loc, box_loc, state, box
                )
                total_distance += box_distance * self.box_priority[agent][box]

        if agent in self.agent_goal_positions:
            total_distance += self.get_distances(
                state, self.agent_goal_positions[agent]
            )[agent_loc.row][agent_loc.col] * get_priority(
                len(self.agent_assigned_to_box[agent])
            )
        return total_distance

    def calculate_box_distance(self, agent_loc, box_loc, state, box):
        box_distance = 0
        if not is_box_close(agent_loc, box_loc):
            box_distance += (
                self.get_distances(state, box_loc)[agent_loc.row][agent_loc.col] - 1
            )
        box_distance += self.get_distances(
            state, self.box_goal_positions[self.box_goal_assigned_to_box[box]]
        )[box_loc.row][box_loc.col]
        return box_distance

    def f(self, state: State) -> float | int:
        return state.g + self.h(state)

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
        self.distances: dict[Pos, list[list[int | float]]] = {}
        for agent, loc in self.agent_goal_positions.items():
            self.get_distances(state=state, position=loc)

        for box_name, loc in self.box_goal_positions.items():
            self.get_distances(state=state, position=loc)

        for box, loc in state.box_locations.items():
            self.get_distances(state=state, position=loc)

    def assign_boxes_to_agents(self, state: State) -> dict[int, list[Box]]:
        agent_assigned_to_box = self.initialize_agent_box_dict()
        for color in set(State.agent_colors):
            agent_boxes = self.create_agent_boxes(state, color)
            while not self.all_boxes_assigned(agent_boxes):
                best_agent = self.find_best_agent(agent_boxes)
                if best_agent is not None:
                    self.assign_box_to_agent(
                        best_agent, agent_boxes, agent_assigned_to_box
                    )
        return agent_assigned_to_box

    @staticmethod
    def initialize_agent_box_dict():
        return {agent: [] for agent in State.agent_box_dict}

    def create_agent_boxes(self, state: State, color: str):
        agent_boxes = {
            agent: []
            for agent in State.agent_box_dict
            if State.agent_colors[agent] == color
        }
        for agent in agent_boxes:
            agent_loc = state.agent_locations[agent]
            agent_boxes[agent] = [
                (box, self.get_distances(state, agent_loc))
                for box in self.get_agent_boxes(agent)
            ]
            agent_boxes[agent].sort(key=lambda x: x[1])
        return agent_boxes

    @staticmethod
    def all_boxes_assigned(agent_boxes):
        return all(not boxes for boxes in agent_boxes.values())

    def find_best_agent(self, agent_boxes):
        eligible_agents = self.get_eligible_agents(agent_boxes)
        return min(
            eligible_agents,
            key=lambda agent: (
                agent_boxes[agent][0][1] if agent_boxes[agent] else float("inf")
            ),
            default=None,
        )

    def assign_box_to_agent(self, best_agent, agent_boxes, agent_assigned_to_box):
        box_to_add = agent_boxes[best_agent].pop(0)[0]
        self.remove_box_from_other_agents(agent_boxes, box_to_add)
        agent_assigned_to_box[best_agent].append(box_to_add)

    @staticmethod
    def get_agent_boxes(agent):
        return [
            box
            for box_name in State.agent_box_dict[agent]
            for box in State.boxes[box_name]
        ]

    @staticmethod
    def get_eligible_agents(agent_boxes):
        min_boxes = min(len(boxes) for boxes in agent_boxes.values())
        return [
            agent for agent, boxes in agent_boxes.items() if len(boxes) == min_boxes
        ]

    @staticmethod
    def remove_box_from_other_agents(agent_boxes, box_to_add):
        for boxes in agent_boxes.values():
            boxes[:] = [(b, t) for (b, t) in boxes if b != box_to_add]

    def assign_boxes_to_goals(self, state: State) -> dict[Box, Box]:
        box_goal_assigned_to_box = {}
        goal_boxes = self.create_goal_boxes(state)

        for box_goal in goal_boxes:
            if goal_boxes[box_goal]:
                new_box = goal_boxes[box_goal].pop(0)[0]
                box_goal_assigned_to_box[new_box] = box_goal
                self.remove_box_from_other_goals(goal_boxes, new_box)

        return box_goal_assigned_to_box

    def create_goal_boxes(self, state: State):
        goal_boxes = {
            box_goal: []
            for box_name in State.boxgoals
            for box_goal in State.boxgoals[box_name]
        }
        for box_goal in goal_boxes:
            goal_boxes[box_goal] = self.get_sorted_boxes_for_goal(state, box_goal)
        return goal_boxes

    def get_sorted_boxes_for_goal(self, state: State, box_goal: Box):
        boxes_for_goal = [
            (box, self.get_distances(state, self.box_goal_positions[box_goal]))
            for box in State.boxes[box_goal[0]]
        ]
        boxes_for_goal.sort(key=lambda x: x[1])
        return boxes_for_goal

    @staticmethod
    def remove_box_from_other_goals(goal_boxes, new_box):
        for box_goal in goal_boxes:
            goal_boxes[box_goal] = [
                (b, t) for (b, t) in goal_boxes[box_goal] if b != new_box
            ]

    def get_distances(self, state: State, position: Pos):
        if position not in self.distances:
            self.distances[position] = HeuristicSimpleDijkstra.create_mapping(
                state,
                position.row,
                position.col,
                len(Location.walls),
                len(Location.walls[0]),
            )
        return self.distances[position]


def get_priority(i: int) -> float:
    return 1 / 2 ** (i + 1)


def get_close_boxes(loc: Location, boxes: dict):
    close_boxes = {}

    for neighbour in Location.get_neighbours(loc):
        for box, box_loc in boxes.items():
            if box_loc == neighbour:
                close_boxes[box] = neighbour

    return close_boxes


def is_box_close(agent_loc: Pos, box_loc: Pos):
    return (abs(agent_loc.row - box_loc.row) == 1 and agent_loc.col == box_loc.col) or (
        abs(agent_loc.col - box_loc.col) == 1 and agent_loc.row == box_loc.row
    )
