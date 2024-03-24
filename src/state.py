import random
from atom import Atom, AgentAt, BoxAt, Free, Location
from color import Color
from action import Action, Move, PossibleAction
from typing import Self


class State:
    _RNG = random.Random(1)
    agent_colors = []
    box_colors = []
    agent_box_dict = {}
    goal_literals: list[Atom] = []

    def __init__(self, literals, time_step=0):
        self.literals: list[Atom] = literals
        self.agent_locations = {lit.agt: lit.loc for lit in self.literals if isinstance(lit, AgentAt)}
        self.time_step = time_step
        self.parent = None
        self.joint_action = None
        self.g = 0
        self._hash = None

    def make_initial_state(server_messages):
        # Read colors.
        server_messages.readline()  # #colors
        agent_colors = [None for _ in range(10)]
        box_colors = [None for _ in range(26)]
        line = server_messages.readline()
        while not line.startswith('#'):
            split = line.split(':')
            color = Color.from_string(split[0].strip())
            entities = [e.strip() for e in split[1].split(',')]
            for e in entities:
                if '0' <= e <= '9':
                    agent_colors[ord(e) - ord('0')] = color
                elif 'A' <= e <= 'Z':
                    box_colors[ord(e) - ord('A')] = color
            line = server_messages.readline()

        literals = []
        num_rows = 0
        num_cols = 0
        level_lines = []
        line = server_messages.readline()
        while not line.startswith('#'):
            level_lines.append(line)
            num_cols = max(num_cols, len(line))
            num_rows += 1
            line = server_messages.readline()

        walls = [[False for _ in range(num_cols)] for _ in range(num_rows)]
        num_agents = 0
        row = 0
        for line in level_lines:
            for col, c in enumerate(line):
                if '0' <= c <= '9':
                    agent = ord(c) - ord('0')
                    literals += [AgentAt(agent, Location(row, col))]
                    num_agents += 1
                elif 'A' <= c <= 'Z':
                    literals += [BoxAt(agent, Location(row, col))]
                elif c == '+' or c == '\n':
                    walls[row][col] = True
                else:
                    # literals += [Free(Location(row,col))]
                    pass
            row += 1

        # Create all rigid literals relating to Locations
        Location.calculate_all_neighbours(walls)
        Free.walls = walls
        # Read goal state.
        # line is currently "#goal".
        goal_literals = []
        line = server_messages.readline()
        row = 0
        while not line.startswith('#'):
            for col, c in enumerate(line):
                if '0' <= c <= '9':
                    agent = ord(c) - ord('0')
                    goal_literals += [AgentAt(agent, Location(row, col))]
                    num_agents += 1
                elif 'A' <= c <= 'Z':
                    goal_literals += [BoxAt(agent, Location(row, col))]

            row += 1
            line = server_messages.readline()

        # End.
        # line is currently "#end".

        State.agent_colors = agent_colors
        State.box_colors = box_colors
        State.agent_box_dict = {i: [chr(j + ord('A')) for j, b in enumerate(box_colors) if b is not None and b == a] for
                                i, a in enumerate(agent_colors) if a is not None}
        State.goal_literals = goal_literals
        # print(literals)
        return State(literals)

    def result(self, joint_action: list[Action]) -> Self:
        copy_literals = self.literals[:]
        for action in joint_action:
            copy_literals = action.apply_effects(copy_literals)

        copy_state = State(copy_literals, self.time_step + 1)
        copy_state.parent = self
        copy_state.joint_action = joint_action[:]
        copy_state.g = self.g + 1
        return copy_state

    def is_goal_state(self) -> bool:
        for goal in self.goal_literals:
            if goal not in self.literals:
                return False
        return True

    def get_expanded_states(self) -> list[Self]:
        num_agents = len(self.agent_locations)

        # Determine list of applicable action for each individual agent.
        applicable_actions = [self.get_applicable_actions(agent) for agent in range(num_agents)]

        # Iterate over joint actions, check conflict and generate child states.
        joint_action = [None for _ in range(num_agents)]
        actions_permutation = [0 for _ in range(num_agents)]
        expanded_states = []
        while True:
            for agent in range(num_agents):
                joint_action[agent] = applicable_actions[agent][
                    actions_permutation[agent]
                ]

            if not self.is_conflicting(joint_action):
                expanded_states.append(self.result(joint_action))

            # Advance permutation.
            done = False
            for agent in range(num_agents):
                if actions_permutation[agent] < len(applicable_actions[agent]) - 1:
                    actions_permutation[agent] += 1
                    break
                else:
                    actions_permutation[agent] = 0
                    if agent == num_agents - 1:
                        done = True

            # Last permutation?
            if done:
                break

        State._RNG.shuffle(expanded_states)
        return expanded_states

    def is_applicable(self, action: Action, literals: list[Atom]) -> bool:
        if isinstance(action, Move):
            return Move(action.agt, action.agtfrom, action.agtto).check_preconditions(literals)
        elif isinstance(action, Action):
            return Action(action.agt).check_preconditions(literals)
        return False

    def get_applicable_actions(self, agent: int) -> Action:
        agtfrom = self.agent_locations[agent]
        possibilities = []
        possible_actions = [Action, Move]
        for action in possible_actions:
            if action is Move:
                for agtto in agtfrom.neighbours:
                    action = Move(agent, agtfrom, agtto)
                    if self.is_applicable(action, self.literals[:]):
                        possibilities.append(Move(agent, agtfrom, agtto))
            elif action is Action:
                possibilities.append(Action(agent))
        return possibilities

    def is_conflicting(self, joint_action: list[Action]) -> bool:
        # This follows the following logic:
        # For all applicable actions ai and aj where the precondition of one is inconsistent with the 
        # effect of the other, either CellCon ict(ai aj) or BoxCon ict(ai aj) holds.
        literals = self.literals[:]
        for agt, action in enumerate(joint_action):
            if self.is_applicable(action, literals):
                literals = action.apply_effects(literals)
            else:
                return True
        return False

    def extract_plan(self) -> list[list[Action]]:
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
            _hash = _hash * prime + hash(tuple(self.literals))
            _hash = _hash * prime + hash(tuple(State.agent_colors))
            _hash = _hash * prime + hash(tuple(State.box_colors))
            _hash = _hash * prime + hash(tuple(State.goal_literals))
            _hash = _hash * prime + hash(self.time_step)
            self._hash = _hash
        return self._hash

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, State):
            return set(self.literals) == set(other.literals) and self.time_step == other.time_step
        return False

    def __repr__(self):
        return f"||{'^'.join(str(lit) for lit in self.literals)}||"
