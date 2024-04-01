from src.domain.state import State
from src.heuristics.heuristic import Heuristic


class HeuristicManhattan(Heuristic):
    def __init__(self, initial_state: "State"):
        super().__init__(initial_state)

    def h(self, state: 'State') -> 'int':
        total_distance = 0
        # Calculate distance from boxes to their goals
        for box_row in range(len(state.boxes)):
            for box_col in range(len(state.boxes[box_row])):
                box = state.boxes[box_row][box_col]
                if box:  # If there's a box at this position
                    for goal, (goal_row, goal_col) in self.box_goal_positions.items():
                        if box == goal:
                            distance = self.calculate_manhattan_distance((box_row, box_col), (goal_row, goal_col))
                            total_distance += distance
                            break

        # Calculate distance from agents to their goals
        for agent_index, (agent_row, agent_col) in enumerate(zip(state.agent_rows, state.agent_cols)):
            agent_goal = str(agent_index)  # Goals are indexed by their integer representation
            if agent_goal in self.agent_goal_positions:
                goal_row, goal_col = self.agent_goal_positions[agent_goal]
                distance = self.calculate_manhattan_distance((agent_row, agent_col), (goal_row, goal_col))
            else:
                min_distance = float('inf')  # Start with infinity to ensure any real distance is smaller
                for goal_ident, (goal_row, goal_col) in self.agent_goal_positions.items():
                    if goal_ident != agent_goal:  # Ensure we're looking at other agents' goals
                        distance = self.calculate_manhattan_distance((agent_row, agent_col), (goal_row, goal_col))
                        min_distance = min(min_distance, distance)
                distance = -min_distance  # Use negative distance to encourage moving away
            total_distance += distance

        return total_distance

    def f(self, state: 'State') -> 'int':
        return self.h(state)

    def __repr__(self):
        return "Manhattan distance heuristic"

    @staticmethod
    def calculate_manhattan_distance(first_position, second_position):
        return abs(first_position[0] - second_position[0]) + abs(first_position[1] - second_position[1])
