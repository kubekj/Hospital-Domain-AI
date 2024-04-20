import itertools
import random

import numpy as np

from src.cbs.cbsaction import CBSActionType, CBSAction
from src.domain.state import State


class CBSState:
    _RNG = random.Random(1)
    goals = []
    walls = []
    agent_colors = []
    box_colors = []

    def __init__(self, agent_rows, agent_cols, boxes):
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
        self.agent_rows = np.array(agent_rows, dtype=int)
        self.agent_cols = np.array(agent_cols, dtype=int)
        self.boxes = np.array(boxes, dtype=object)

        self.boxes_map = {}
        for (row, col), value in np.ndenumerate(self.boxes):
            if 'A' <= value <= 'Z':  # Check if the current cell contains a box
                self.boxes_map[value] = (row, col)

        self.parent = None
        self.joint_action = None
        self.g = 0
        self._hash = None

    @staticmethod
    def make_initial_state(server_messages):
        agent_colors, box_colors = State.read_colors(server_messages)
        _, num_rows, num_cols, walls = State.read_level(server_messages)

        State.agent_colors = agent_colors
        State.box_colors = box_colors
        State.walls = walls

    def result(self, joint_action: "[NPAction, ...]") -> "CBSState":
        """
        Returns the state resulting from applying joint_action in this state.
        Precondition: Joint action must be applicable and non-conflicting in this state.
        """
        # Copy this state.
        copy_agent_rows = np.copy(self.agent_rows)
        copy_agent_cols = np.copy(self.agent_cols)
        copy_boxes = np.copy(self.boxes)

        for agent, action in enumerate(joint_action):
            delta_row, delta_col = action.agent_row_delta, action.agent_col_delta

            if action.action_type == CBSActionType.NoOp:
                continue

            if action.action_type in [CBSActionType.Move, CBSActionType.Push, CBSActionType.Pull]:
                copy_agent_rows[agent] += delta_row
                copy_agent_cols[agent] += delta_col

            if action.action_type in [CBSActionType.Push, CBSActionType.Pull]:
                if action.type == CBSActionType.Push:
                    box_row, box_col = copy_agent_rows[agent], copy_agent_cols[agent]
                else:  # Pull
                    box_row, box_col = copy_agent_rows[agent] - delta_row, copy_agent_cols[agent] - delta_col

                # Calculate new box position
                new_box_row = box_row + action.box_row_delta
                new_box_col = box_col + action.box_col_delta

                # Move the box
                box = copy_boxes[box_row, box_col]
                copy_boxes[box_row, box_col] = ''
                copy_boxes[new_box_row, new_box_col] = box

                self.boxes_map[box] = (new_box_row, new_box_col)

        copy_state = CBSState(copy_agent_rows, copy_agent_cols, copy_boxes)
        copy_state.parent = self
        copy_state.joint_action = joint_action[:]
        copy_state.g = self.g + 1

        return copy_state

    def is_goal_state(self) -> bool:
        """
        Checks if the current state matches the goal state.
        The goal state is defined by both box positions and agent positions:
        - Each box must match the character in the goals array (A-Z for boxes).
        - Each agent must match the numeric position specified in the goals array (0-9 for agents).
        """
        for (row, col), goal in np.ndenumerate(CBSState.goals):
            if 'A' <= goal <= 'Z':
                if self.boxes[row, col] != goal:
                    return False
            elif '0' <= goal <= '9':
                agent_index = int(goal)
                if not (self.agent_rows[agent_index] == row and self.agent_cols[agent_index] == col):
                    return False

        return True

    def get_expanded_states(self) -> "[NPState, ...]":
        num_agents = len(self.agent_rows)

        # Determine list of applicable action for each individual agent.
        applicable_actions = [
            [action for action in CBSAction if self.is_applicable(agent, action)] for agent in range(num_agents)
        ]

        product_of_actions = itertools.product(*applicable_actions)

        expanded_states = []

        # Iterate over each combination of actions
        for joint_action in product_of_actions:
            if not self.is_conflicting(joint_action):
                expanded_states.append(self.result(joint_action))

        CBSState._RNG.shuffle(expanded_states)

        return expanded_states

    def is_applicable(self, agent: int, action: "CBSAction") -> bool:
        agent_row = self.agent_rows[agent]
        agent_col = self.agent_cols[agent]

        if action.action_type == CBSActionType.NoOp:
            return True

        destination_row = agent_row + action.agent_row_delta
        destination_col = agent_col + action.agent_col_delta

        if action.action_type == CBSActionType.Move:
            return self.is_free(destination_row, destination_col)

        elif action.action_type == CBSActionType.Push:
            if not self.is_within_bounds(destination_row, destination_col):
                return False
            box = self.boxes[destination_row, destination_col]
            if box:  # Check if box exists at the location
                next_row = destination_row + action.box_row_delta
                next_col = destination_col + action.box_col_delta
                return (CBSState.box_colors[ord(box) - ord('A')] == CBSState.agent_colors[agent] and
                        self.is_free(next_row, next_col))

        elif action.action_type == CBSActionType.Pull:
            source_row = agent_row - action.box_row_delta
            source_col = agent_col - action.box_col_delta
            if not self.is_within_bounds(source_row, source_col):
                return False
            box = self.boxes[source_row, source_col]
            if box and self.is_free(destination_row, destination_col):  # Check if box exists and destination is free
                return CBSState.box_colors[ord(box) - ord('A')] == CBSState.agent_colors[agent]

        return False

    def is_within_bounds(self, row, col):
        return 0 <= row < self.boxes.shape[0] and 0 <= col < self.boxes.shape[1]

    def is_conflicting(self, joint_action: "[NPAction, ...]") -> "bool":
        num_agents = len(self.agent_rows)
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
        for agent in range(num_agents):
            action = joint_action[agent]
            agent_row = self.agent_rows[agent]
            agent_col = self.agent_cols[agent]

            if action.action_type == CBSActionType.NoOp:
                pass

            elif action.action_type == CBSActionType.Move:
                destination_rows[agent] = agent_row + action.agent_row_delta
                destination_cols[agent] = agent_col + action.agent_col_delta

            elif action.action_type == CBSActionType.Push:
                destination_rows[agent] = agent_row + action.agent_row_delta
                destination_cols[agent] = agent_col + action.agent_col_delta
                box_rows[agent] = agent_row + joint_action[agent].agent_row_delta
                box_cols[agent] = agent_col + joint_action[agent].agent_col_delta

            elif action.action_type == CBSActionType.Pull:
                destination_rows[agent] = agent_row + action.agent_row_delta
                destination_cols[agent] = agent_col + action.agent_col_delta
                box_rows[agent] = agent_row - joint_action[agent].box_row_delta
                box_cols[agent] = agent_row - joint_action[agent].box_col_delta

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
        return not CBSState.walls[row][col] and self.boxes[row][col] == "" and self.agent_at(row, col) is None

    def agent_at(self, row: "int", col: "int") -> "chr":
        """
        Returns the agent number (0-indexed) at the given row and column, or None if no agent is there.
        """
        for agent in range(len(self.agent_rows)):
            if self.agent_rows[agent] == row and self.agent_cols[agent] == col:
                return chr(agent + ord("0"))
        return None

    def extract_plan(self) -> "[NPAction, ...]":
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
            _hash = _hash * prime + hash(tuple(self.agent_rows))
            _hash = _hash * prime + hash(tuple(self.agent_cols))
            _hash = _hash * prime + hash(tuple(CBSState.agent_colors))
            _hash = _hash * prime + hash(tuple(tuple(row) for row in self.boxes))
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
        if self.agent_rows != other.agent_rows:
            return False
        if self.agent_cols != other.agent_cols:
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
