import copy
import itertools
import random

import numpy as np

from src.cbs.cbsaction import CBSActionType, CBSAction
from src.cbs.cbsagent import CBSAgent
from src.cbs.cbsbox import CBSBox


class CBSState:
    _RNG = random.Random(1)
    agent_colors = list()
    box_colors = list()
    walls = list()
    goals = list()
    goals_coords = list()
    agent_box_dict = dict()

    def __init__(self, agents, boxes):
        """
        Constructs an initial state.
        Arguments are not copied, and therefore should not be modified after being passed in.

        The lists walls, boxes, and goals are indexed from top-left of the level, row-major order (row, col).
               Col 0  Col 1  Col 2  Col 3
        Row 0: (0,0)  (0,1)  (0,2)  (0,3)  ...
        Row 1: (1,0)  (1,1)  (1,2)  (1,3)  ...
        Row 2: (2,0)  (2,1)  (2,2)  (2,3)  ...
        ...

        For example, State.walls[2] is a list of booleans for the third row.
        State.walls[row][col] is True if there's a wall at (row, col).

        The agent rows and columns are indexed by the agent number.
        For example, State.agent_rows[0] is the row location of agent '0'.

        Note: The state should be considered immutable after it has been hashed, e.g. added to a dictionary or set.
        """
        self.agents = agents
        self.boxes = boxes
        self.parent = None
        self.joint_action = None
        self.g = 0
        self._hash = None

    def result(self, joint_action):
        # Create a deep copy of the current agents and boxes
        new_agents = copy.deepcopy(self.agents)
        new_boxes = copy.deepcopy(self.boxes)

        # Iterate over each agent and the corresponding action
        for agent, action in zip(new_agents, joint_action):
            # If the action is a push or pull, check if the box is in the agent's list of boxes
            if action.action_type in [CBSActionType.Push, CBSActionType.Pull]:
                for box in agent.boxes:
                    box_row, box_col = box.position
                    # Check if the box is in the direction of the action
                    if (box_row - agent.position[0] == action.box_row_delta and
                            box_col - agent.position[1] == action.box_col_delta):
                        # Move the box in the direction of the action for a push
                        # and in the opposite direction for a pull
                        direction = 1 if action.action_type == CBSActionType.Push else -1
                        box.move(direction * action.box_row_delta, direction * action.box_col_delta)
                        break
            # Move the agent in the direction of the action
            agent.move(action.agent_row_delta, action.agent_col_delta)

        copy_state = CBSState(new_agents, new_boxes)
        copy_state.parent = self
        copy_state.joint_action = joint_action[:]
        copy_state.g = self.g + 1
        self._hash = self.__hash__()

        return copy_state

    # def result(self, joint_action):
    #     """
    #     This method applies a joint action to the current state and returns a new state.
    #
    #     Parameters:
    #     joint_action (list): A list of actions, one for each agent.
    #
    #     Returns:
    #     CBSState: A new state after applying the joint action.
    #
    #     """
    #
    #     # Create a copy of the current agents and boxes
    #     new_agents = copy.deepcopy(self.agents)
    #     new_boxes = copy.deepcopy(self.boxes)
    #
    #     # Iterate over each agent and the corresponding action
    #     for agent, action in zip(new_agents, joint_action):
    #         # If the action is a push, move the box in the direction of the action
    #         if action.action_type == CBSActionType.Push:
    #             box = new_boxes[action.box_label]
    #             box.move(action.box_row_delta, action.box_col_delta)
    #         # If the action is a pull, move the box in the opposite direction of the action
    #         elif action.action_type == CBSActionType.Pull:
    #             box = new_boxes[action.box_label]
    #             box.move(-action.box_row_delta, -action.box_col_delta)
    #         # Move the agent in the direction of the action
    #         agent.move(action.agent_row_delta, action.agent_col_delta)
    #
    #     return CBSState(new_agents, new_boxes)

    def is_goal_state(self) -> bool:
        """
        Checks if the current state matches the goal state.
        The goal state is defined by both box positions and agent positions:
        - Each box must match the character in the goals array (A-Z for boxes).
        - Each agent must match the numeric position specified in the goals array (0-9 for agents).
        """
        for agent in self.agents:
            if not agent.is_at_goal():
                return False
        for box in self.boxes:
            for goal_coord in self.goals_coords:
                if not box.is_at_goal(goal_coord):
                    return False
        return True

    def get_expanded_states(self) -> "[CBSState, ...]":
        # Determine list of applicable action for each individual agent.
        applicable_actions = [
            [action for action in CBSAction if self.is_applicable(agent, action)] for agent in self.agents
        ]

        product_of_actions = itertools.product(*applicable_actions)

        expanded_states = []

        # Iterate over each combination of actions
        for joint_action in product_of_actions:
            if not self.is_conflicting(joint_action):
                expanded_states.append(self.result(joint_action))

        CBSState._RNG.shuffle(expanded_states)

        return expanded_states

    def is_applicable(self, agent: CBSAgent, action: "CBSAction") -> bool:
        agent_row = agent.position[0]
        agent_col = agent.position[1]

        if action.action_type == CBSActionType.NoOp:
            return True

        destination_row = agent_row + action.agent_row_delta
        destination_col = agent_col + action.agent_col_delta

        box: CBSBox = None

        if action.action_type == CBSActionType.Move:
            return self.is_free(destination_row, destination_col)

        elif action.action_type == CBSActionType.Push:
            for b in self.boxes:
                if tuple(b.position) == (destination_row, destination_col):                    
                    box = b
                    break
            if box:  # Check if box exists at the location
                next_row = destination_row + action.box_row_delta
                next_col = destination_col + action.box_col_delta
                return agent.color == box.color and self.is_free(next_row, next_col)

        elif action.action_type == CBSActionType.Pull:
            source_row = agent_row - action.box_row_delta
            source_col = agent_col - action.box_col_delta
            for b in self.boxes:
                if tuple(b.position) == (agent_row - action.box_row_delta, agent_col - action.box_col_delta):
                    box = b
                    break
            if box and self.is_free(destination_row, destination_col):  # Check if box exists and destination is free
                return agent.color == box.color

        return False

    def is_conflicting(self, joint_action: "[CBSAction, ...]") -> "bool":
        num_agents = len(self.agents)
        destination_rows = [
            None for _ in range(num_agents)
        ]  # row of new cell to become occupied by action
        destination_cols = [
            None for _ in range(num_agents)
        ]  # column of new cell to become occupied by action
        box_rows = [
            None for _ in range(num_agents)
        ]  # current row of box moved by action
        box_cols = [
            None for _ in range(num_agents)
        ]  # current column of box moved by action

        # Collect cells to be occupied and boxes to be moved.
        for agent in self.agents:
            agent_row = agent.position[0]
            agent_col = agent.position[1]
            agent_id = agent.id
            action = joint_action[agent_id]

            if action.action_type == CBSActionType.NoOp:
                pass

            elif action.action_type == CBSActionType.Move:
                destination_rows[agent_id] = agent_row + action.agent_row_delta
                destination_cols[agent_id] = agent_col + action.agent_col_delta

            elif action.action_type == CBSActionType.Push:
                destination_rows[agent_id] = agent_row + action.agent_row_delta
                destination_cols[agent_id] = agent_col + action.agent_col_delta
                box_rows[agent_id] = agent_row + joint_action[agent_id].agent_row_delta
                box_cols[agent_id] = agent_col + joint_action[agent_id].agent_col_delta

            elif action.action_type == CBSActionType.Pull:
                destination_rows[agent_id] = agent_row + action.agent_row_delta
                destination_cols[agent_id] = agent_col + action.agent_col_delta
                box_rows[agent_id] = agent_row - joint_action[agent_id].box_row_delta
                box_cols[agent_id] = agent_row - joint_action[agent_id].box_col_delta

        for a1 in range(num_agents):
            if joint_action[a1] is CBSAction.NoOp:
                continue

            for a2 in range(a1 + 1, num_agents):
                if joint_action[a2] is CBSAction.NoOp:
                    continue

                # Moving into same cell?
                if (
                        destination_rows[a1] == destination_rows[a2]
                        and destination_cols[a1] == destination_cols[a2]
                ):
                    return True
                # Moving a box into a cell that will be occupied by a box?
                if joint_action[a1].action_type == CBSActionType.Push:
                    if (box_rows[a1] + joint_action[a1].box_row_delta == destination_rows[a2]
                            and box_cols[a1] + joint_action[a1].box_col_delta == destination_cols[a2]):
                        return True
                if joint_action[a2].action_type == CBSActionType.Push:
                    if (box_rows[a2] + joint_action[a2].box_row_delta == destination_rows[a1]
                            and box_cols[a2] + joint_action[a2].box_col_delta == destination_cols[a1]):
                        return True
        return False

    def is_free(self, row: "int", col: "int") -> "bool":
        """
        Returns True if the cell is free (not a wall, box, or agent), False otherwise.
        """
        return not CBSState.walls[row][col] and self.box_at(row, col) == '' and self.agent_at(row, col) == -1

    def box_at(self, row: "int", col: "int") -> chr:
        """
        Returns the box character at the given row and column, or None if no box is there.
        """
        for box in self.boxes:
            if box.position[0] == row and box.position[1] == col:
                return box.label
        return None

    def agent_at(self, row: "int", col: "int") -> int:
        """
        Returns the agent id (0-indexed) at the given row and column, or None if no agent is there.
        """
        for agent in self.agents:
            if agent.position[0] == row and agent.position[1] == col:
                return agent.id
        return None

    def extract_plan(self) -> "[CBSAction, ...]":
        """
        Extract a plan from the current state.
        """
        plan = [None for _ in range(self.g)]
        state = self
        while state.joint_action is not None:
            plan[state.g - 1] = state.joint_action
            state = state.parent
        return plan

    def __hash__(self):
        if self._hash is None:
            prime = 31
            _hash = 1
            _hash = _hash * prime + hash(tuple(self.agents))
            _hash = _hash * prime + hash(tuple(self.boxes))
            _hash = _hash * prime + hash(tuple(CBSState.agent_colors))
            _hash = _hash * prime + hash(tuple(CBSState.box_colors))
            _hash = _hash * prime + hash(tuple(tuple(row) for row in CBSState.goals))
            _hash = _hash * prime + hash(tuple(tuple(row) for row in CBSState.walls))
            self._hash = _hash
        return self._hash

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, CBSState):
            return False
        if self.agents != other.agents:
            return False
        if CBSState.agent_colors != other.agent_colors:
            return False
        if CBSState.walls != other.walls:
            return False
        if self.boxes != other.boxes:
            return False
        if CBSState.box_colors != other.box_colors:
            return False
        if CBSState.goals != other.goals:
            return False
        return True

    def __repr__(self):
        lines = []
        for row in range(len(self.boxes)):
            line = []
            for col in range(len(self.boxes[row])):
                if self.boxes[row][col] != "":
                    line.append(self.boxes[row][col])
                elif CBSState.walls[row][col] is not None:
                    line.append("+")
                elif self.agent_at(row, col) is not None:
                    line.append(self.agent_at(row, col))
                else:
                    line.append(" ")
            lines.append("".join(line))
        return "\n".join(lines)
