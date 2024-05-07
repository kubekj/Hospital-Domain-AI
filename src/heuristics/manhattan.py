from src.domain.atom import AtomType, atoms_by_type
from src.domain.state import State
from src.heuristics.heuristic import Heuristic


class HeuristicManhattan(Heuristic):
    def __init__(self, initial_state: "State"):
        super().__init__(initial_state)

    def h(self, state: 'State') -> 'int':
        total_distance = 0
        agent_positions = atoms_by_type(state.literals, AtomType.AGENT_AT)
        box_positions = atoms_by_type(state.literals, AtomType.BOX_AT)

        # Calculate distance from boxes to their goals
        for box, (box_row, box_col) in box_positions.items():
            if box in self.box_goal_positions:
                goal_loc = self.box_goal_positions[box]
                distance = self.calculate_manhattan_distance((box_row, box_col), (goal_loc.row, goal_loc.col))
                total_distance += distance

        # Calculate distance from agents to their goals
        for agent, (agent_row, agent_col) in agent_positions.items():
            if agent in self.agent_goal_positions:
                goal_loc = self.agent_goal_positions[agent]
                distance = self.calculate_manhattan_distance((agent_row, agent_col), (goal_loc.row, goal_loc.col))
                total_distance += distance

        return total_distance

    def f(self, state: 'State') -> 'int':
        return self.h(state)

    def __repr__(self):
        return "Manhattan distance heuristic"

    @staticmethod
    def calculate_manhattan_distance(first_position, second_position):
        return abs(first_position[0] - second_position[0]) + abs(first_position[1] - second_position[1])


