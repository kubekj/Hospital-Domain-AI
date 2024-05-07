from src.domain.atom import AgentAt, Box, BoxAt, Free, Location
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
        # print(Free.walls)
        for row in range(len(Free.walls)):
            for col in range(len(Free.walls[0])):
                if not Free.walls[row][col]:
                    self.name_choke_points(row, col, 0)
                    break_outer_loop = True
                    break
            if break_outer_loop:
                break
        
        
        self.assign_boxes_to_agents(initial_state)

        self.box_priority = {}
        for agent, agent_boxes in self.agent_assigned_to_box.items():
            agent_loc = initial_state.agent_locations[agent]
            sorted_boxes = sorted(
                        agent_boxes,
                        key=lambda b: self.initial_distances_from_box[b][agent_loc.row][
                            agent_loc.col
                        ],
                    )
            self.box_priority[agent] = {box:getPriority(i) for i, box in enumerate(sorted_boxes)}


    def h(self, state: State) -> int:
        total_distance = 0
        agents = {
            lit.agt: lit.loc for lit in state.literals if isinstance(lit, AgentAt)
        }
        boxes = {lit.box: lit.loc for lit in state.literals if isinstance(lit, BoxAt)}

        for agt, box in enumerate(state.recalculateDistanceOfBox):
            if box != None:
                # print(f"Recalculating box {box} last moved by agent {agt}")
                self.initial_distances_from_box[box] = (
                    HeuristicSimpleDijkstra.create_mapping(state,
                                                        boxes[box].row,
                                                        boxes[box].col,
                                                        len(Free.walls),
                                                        len(Free.walls[0])))

        for agent, agent_loc in agents.items():
            try:
                boxes_not_in_goal = [b for b_name in State.agent_box_dict[agent] for b in State.boxes[b_name] if
                                     b_name in self.box_goal_positions and
                                        self.box_goal_positions[b_name] != boxes[b]]
            except Exception as exc:
                print(State.agent_box_dict)
                print(self.box_goal_positions)
                print('H' in self.box_goal_positions)
                raise Exception(exc)

            for b in self.agent_assigned_to_box[agent]:
                box_distance = 0
                # Distance from the agent to the box
                box_distance += self.initial_distances_from_box[b][
                        agent_loc.row
                    ][agent_loc.col] - 1 
                # Distance from the box to its goal
                box_distance += self.distances_from_box_goals[b.name]
                total_distance += box_distance

            if len(boxes_not_in_goal):
                close_boxes = get_close_boxes(
                    agent_loc,
                    {b: boxes[b] for b in boxes if b in State.agent_box_dict[agent]},
                )
                if len(close_boxes) == 0:
                    # Distance of the agent to the closest box
                    closest_box = min(
                        boxes_not_in_goal,
                        key=lambda b: self.initial_distances_from_box[b][agent_loc.row][
                            agent_loc.col
                        ],
                    )
                    total_distance += self.initial_distances_from_box[closest_box][
                        agent_loc.row
                    ][agent_loc.col] - 1

                # Distance of boxes to their goals
                for other_box in boxes_not_in_goal:
                    box_position = boxes[other_box]
                    total_distance += self.distances_from_box_goals[other_box][
                        box_position.row
                    ][box_position.col]

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
            if agent in self.distances_from_agent_goals:
                total_distance += (
                    self.distances_from_agent_goals[agent][agent_loc.row][agent_loc.col]
                    * getPriority(len(self.box_priority[agent]))
                )

        return total_distance

    def f(self, state: State) -> int:
        return self.h(state)

    def __repr__(self):
        return "Dijkstra heuristic"

    def name_choke_points(self, row, col, id):
        if Free.walls[row][col]:
            print("ERROR: Started name_choke_points in a wall.")
            return
        possible_moves = []
        if len(Free.walls) > row + 1 and not Free.walls[row + 1][col]:
            possible_moves += [(row + 1, col)]

        if 0 <= row - 1 and not Free.walls[row - 1][col]:
            possible_moves += [(row - 1, col)]

        if len(Free.walls[row]) > col + 1 and not Free.walls[row][col + 1]:
            possible_moves += [(row, col + 1)]

        if 0 <= col - 1 and not Free.walls[row][col - 1]:
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
        num_rows = len(Free.walls)
        num_cols = len(Free.walls[0])
        self.distances_from_agent_goals:dict[int, int] = {}
        self.distances_from_box_goals:dict[str, int] = {}
        self.initial_distances_from_box:dict[Box, int] = {}
        for agent, loc in self.agent_goal_positions.items():
            self.distances_from_agent_goals[agent] = (
                HeuristicSimpleDijkstra.create_mapping(
                    state, loc.row, loc.col, num_rows, num_cols
                )
            )
        for box_name, loc in self.box_goal_positions.items():
            self.distances_from_box_goals[box_name] = HeuristicSimpleDijkstra.create_mapping(
                state, loc.row, loc.col, num_rows, num_cols
            )

        boxes = {lit.box: lit.loc for lit in state.literals if isinstance(lit, BoxAt)}
        for box, loc in boxes.items():
            self.initial_distances_from_box[box] = (
                HeuristicSimpleDijkstra.create_mapping(
                    state, loc.row, loc.col, num_rows, num_cols
                )
            )

    def assign_boxes_to_agents(self, state:State):
        self.agent_assigned_to_box:dict[int,list[Box]] = {}
        # for agent, agent_boxes_names in State.agent_box_dict:
        #     agent_loc = initial_state.agent_locations[agent]
        #     sorted_boxes = sorted(
        #                 [b for b_name in agent_boxes_names for b in State.boxes[b_name]],
        #                 key=lambda b: self.initial_distances_from_box[b][agent_loc.row][
        #                     agent_loc.col
        #                 ],
        #             )
                
        for agent in State.agent_box_dict:
            self.agent_assigned_to_box[agent] = []

        for color in set(State.agent_colors):
            # Create a list of boxes sorted by color matching and distance to each agent
            agent_boxes:dict[int, list[(Box,int)]] = {agent: [] for agent in State.agent_box_dict if State.agent_colors[agent] == color}
            for agent in agent_boxes:
                agent_loc = state.agent_locations[agent]
                for box in [box for box_name in State.agent_box_dict[agent] for box in State.boxes[box_name]]:
                    agent_boxes[agent].append((box, self.initial_distances_from_box[box][agent_loc.row][agent_loc.col]))

            # Sort each agent's list of boxes by distance
            for agent in agent_boxes:
                agent_boxes[agent].sort(key=lambda x: x[1])

            # Assignment process using the new rules
            all_assigned = False
            while not all_assigned:
                all_assigned = True
                # Determine the minimum number of boxes assigned to any agent
                min_boxes = min(len(self.agent_assigned_to_box[agent]) for agent in State.agent_box_dict)

                # Collect eligible agents who either have 'min_boxes' or everyone if all are the same
                eligible_agents = [agent for agent in State.agent_box_dict if len(self.agent_assigned_to_box[agent]) == min_boxes]

                # From the eligible agents, pick the agent with the closest box
                best_agent = None
                best_box_distance = float('inf')

                for agent in eligible_agents:
                    if agent_boxes[agent]:
                        all_assigned = False
                        if agent_boxes[agent][0][1] < best_box_distance:
                            best_box_distance = agent_boxes[agent][0][1]
                            best_agent = agent
                        # Tiebreaker on agent ID if distances are equal
                        elif agent_boxes[agent][0][1] == best_box_distance:
                            if best_agent is None or agent < best_agent:
                                best_agent = agent

                # Assign the closest box to the best agent if one is found
                if best_agent is not None:
                    box_to_add:Box = agent_boxes[best_agent].pop(0)[0]
                    for a in agent_boxes:
                        if box_to_add in (b for (b,_) in agent_boxes[a]):
                            agent_boxes[a].remove(box_to_add)
                    self.agent_assigned_to_box[best_agent].append(box_to_add)
def getPriority(i):
    return 1 / 2**(i+1)

def get_close_boxes(loc: Location, boxes: dict):
    close_boxes = {}

    for neig in loc.neighbours:
        for box, box_loc in boxes.items():
            if box_loc == neig:
                close_boxes[box] = neig

    return close_boxes
