from typing import Tuple
from src.domain.atom import Atom, Box, Location, AtomType, Pos, atoms_by_type
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
        
        
        self.agent_assigned_to_box:dict[int, list[Box]] = self.assign_boxes_to_agents(initial_state)
        self.boxgoal_assigned_to_box:dict[Box, Box] = self.assign_boxes_to_goals(initial_state)

        self.box_priority: dict[int, dict[Box, float]] = {}
        for agent, agent_boxes in self.agent_assigned_to_box.items():
            agent_loc = initial_state.agent_locations[agent]
            sorted_boxes = sorted(
                        agent_boxes,
                        key=lambda b: self.distances[initial_state.box_locations[b]][agent_loc.row][
                            agent_loc.col
                        ],
                    )
            self.box_priority[agent] = {box:getPriority(len(sorted_boxes) - i) for i, box in enumerate(sorted_boxes)}


    def h(self, state: State) -> float|int:
        total_distance = 0

        # TODO: Delete if not needed. It didn't seem to do anything before the merge, and somehow made things worse afterwards.
        for agt, box in enumerate(state.recalculateDistanceOfBox):
            if box != None:
                # print(f"Recalculating box {box} last moved by agent {agt}")
                self.getDistances(state, state.box_locations[box])
                state.recalculateDistanceOfBox[agt] = None

        for agent, agent_loc in state.agent_locations.items():
            try:
                boxes_not_in_goal = [b for b_name in State.agent_box_dict[agent] for b in State.boxes[b_name] if
                                     b_name in self.box_goal_positions and
                                         self.box_goal_positions[self.boxgoal_assigned_to_box[b][0]] != state.box_locations[b]]
            except Exception as exc:
                print("#",State.agent_box_dict)
                print("#",self.box_goal_positions)
                print("#",State.boxes)
                raise Exception(exc)

            for box in self.agent_assigned_to_box[agent]:
                if box in self.boxgoal_assigned_to_box and box in boxes_not_in_goal:
                    box_loc = state.box_locations[box]
                    box_distance = 0
                    # Distance from the agent to the box
                    if not isBoxClose(agent_loc, box_loc):
                        box_distance += self.getDistances(state,box_loc)[
                                agent_loc.row
                            ][agent_loc.col] - 1 
                    # Distance from the box to its goal
                    
                    box_distance += self.getDistances(state, self.box_goal_positions[self.boxgoal_assigned_to_box[box][0]])[box_loc.row][box_loc.col]
                    total_distance += box_distance * self.box_priority[agent][box]

            if agent in self.agent_goal_positions:
                total_distance += (
                    self.getDistances(state, self.agent_goal_positions[agent])[agent_loc.row][agent_loc.col]
                    * getPriority(1)
                )

        return total_distance

    def f(self, state: State) -> float|int:
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
        self.distances:dict[Pos, list[list[int|float]]] = {}
        for agent, loc in self.agent_goal_positions.items():
            self.getDistances(state=state, position=loc)

        for box_name, loc in self.box_goal_positions.items():
            self.getDistances(state=state, position=loc)

        for box, loc in state.box_locations.items():
            self.getDistances(state=state, position=loc)

    def assign_boxes_to_agents(self, state:State) -> dict[int,list[Box]]:
        agent_assigned_to_box:dict[int,list[Tuple[int, int]]] = {}
                
        for agent in State.agent_box_dict:
            agent_assigned_to_box[agent] = []

        for color in set(State.agent_colors):
            # Create a list of boxes sorted by color matching and distance to each agent
            agent_boxes:dict[int, list[tuple[Box,int]]] = {agent: [] for agent in State.agent_box_dict if State.agent_colors[agent] == color}
            for agent in agent_boxes:
                agent_loc = state.agent_locations[agent]
                for box in [box for box_name in State.agent_box_dict[agent] for box in State.boxes[box_name]]:
                    agent_boxes[agent].append((box, self.distances[state.box_locations[box]][agent_loc.row][agent_loc.col]))

            # Sort each agent's list of boxes by distance
            for agent in agent_boxes:
                agent_boxes[agent].sort(key=lambda x: x[1])

            # Assignment process using the new rules
            all_assigned = False
            while not all_assigned:
                all_assigned = True
                # Determine the minimum number of boxes assigned to any agent
                temp = [len(agent_assigned_to_box[agent]) for agent in State.agent_box_dict if State.agent_colors[agent] == color]
                if len(temp) == 0:
                    continue
                min_boxes = min(temp)

                # Collect eligible agents who either have 'min_boxes' or everyone if all are the same
                eligible_agents = [agent for agent in State.agent_box_dict if len(agent_assigned_to_box[agent]) == min_boxes and State.agent_colors[agent] == color]

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
                    box_to_add:Atom = agent_boxes[best_agent].pop(0)[0]
                    for a in agent_boxes:
                        if box_to_add in (b for (b,_) in agent_boxes[a]):
                            filtered = [(b,t) for (b,t) in agent_boxes[a] if b == box_to_add]
                            for f in filtered:
                                agent_boxes[a].remove(f)
                    agent_assigned_to_box[best_agent].append(box_to_add)
        return agent_assigned_to_box

    def assign_boxes_to_goals(self, state: State) -> dict[Box, Box]:
        boxgoal_assigned_to_box:dict[Box, Box] = {}
        
        goal_boxes: dict[Box, list[tuple[Box, int|float]]] = {boxgoal: [] for box_name in State.boxgoals for boxgoal in State.boxgoals[box_name]}
        for box_goal in goal_boxes:
            for box in State.boxes[box_goal[0]]:
                box_loc = state.box_locations[box]
                goal_boxes[box_goal].append((box, self.getDistances(state, self.box_goal_positions[box_goal[0]])[box_loc.row][box_loc.col]))

        # Sort each agent's list of boxes by distance
        for box_goal in goal_boxes:
            goal_boxes[box_goal].sort(key=lambda x: x[1])
        
        for box_goal in goal_boxes:
            if len(goal_boxes[box_goal]) == 0:
                continue
            new_box = goal_boxes[box_goal].pop(0)[0]
            # Dict[Box,BoxGoal] 
            boxgoal_assigned_to_box[new_box] = box_goal
            for box_goal_2 in goal_boxes:
                if new_box in [b for (b,_) in goal_boxes[box_goal_2]]:
                    filtered = [(b,t) for (b,t) in goal_boxes[box_goal_2] if b == new_box]
                    for f in filtered:
                        goal_boxes[box_goal_2].remove(f)
        return boxgoal_assigned_to_box

    def getDistances(self, state: State, position: Pos):
        if position not in self.distances:
            self.distances[position] = HeuristicSimpleDijkstra.create_mapping(
                    state, position.row, position.col, len(Location.walls), len(Location.walls[0])
                )
        return self.distances[position]

def getPriority(i: int) -> float:
    return 2**(i+1)

def get_close_boxes(loc: Location, boxes: dict):
    close_boxes = {}

    for neig in Location.get_neighbours(loc):
        for box, box_loc in boxes.items():
            if box_loc == neig:
                close_boxes[box] = neig

    return close_boxes

def isBoxClose(agent_loc: Pos, box_loc: Pos):
    return (abs(agent_loc.row - box_loc.row) == 1 and agent_loc.col == box_loc.col) or \
           (abs(agent_loc.col - box_loc.col) == 1 and agent_loc.row == box_loc.row)