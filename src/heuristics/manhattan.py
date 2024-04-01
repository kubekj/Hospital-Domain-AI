from src.domain.atom import AgentAt, BoxAt
from src.domain.state import State
from src.heuristics.heuristic import Heuristic


class HeuristicManhattan(Heuristic):
    def __init__(self, initial_state: "State"):
        super().__init__(initial_state)

    def h(self, state: 'State') -> 'int':
        total_distance = 0
        agent_positions = self.extract_agent_positions(state)
        box_positions = self.extract_box_positions(state)

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

    @staticmethod
    def extract_agent_positions(state: 'State'):
        agent_positions = {}
        for lit in state.literals:
            if isinstance(lit, AgentAt):
                agent_positions[lit.agt] = (lit.loc.row, lit.loc.col)
        return agent_positions

    @staticmethod
    def extract_box_positions(state: 'State'):
        box_positions = {}
        for lit in state.literals:
            if isinstance(lit, BoxAt):
                box_positions[lit.box] = (lit.loc.row, lit.loc.col)
        return box_positions

