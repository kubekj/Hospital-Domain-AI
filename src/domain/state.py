import random
from typing import Optional, Self

from src.domain.action import Action, Move, Pull, Push
from src.domain.atom import Atom, Location, AtomType, atoms_by_type, encode_atom_pos
from src.utils.level_parser import Parser


class State:
    _RNG = random.Random(1)
    agent_colors = []
    box_colors = []
    agent_box_dict = {}
    goal_literals: set[Atom] = set()

    def __init__(self, literals):
        self.literals: set[Atom] = literals
        self.agent_locations = atoms_by_type(self.literals, AtomType.AGENT_AT)
        self.parent = None
        self.joint_action = None
        self.g = 0
        self._hash = None

        self.lastMovedBox = [None] * len(self.agent_locations)
        self.recalculateDistanceOfBox = [None] * len(self.agent_locations)

    @staticmethod
    def make_initial_state(server_messages):
        agent_colors, box_colors = Parser.read_colors(server_messages)
        literals, num_rows, num_cols, walls = Parser.read_level(server_messages)
        goal_literals = Parser.read_goal_state(server_messages)

        State.agent_colors = agent_colors
        State.box_colors = box_colors
        State.agent_box_dict = Parser.create_agent_box_dict(agent_colors, box_colors)
        State.goal_literals = goal_literals

        return State(literals)

    def result(self, joint_action: list[Action], copy_literals: Optional[set[Atom]] = None) -> Self:
        calc_results = False
        if copy_literals is None:
            calc_results = True
            copy_literals = set(self.literals)

        copy_recalculateDistanceOfBox = self.recalculateDistanceOfBox[:]
        copy_lastMovedBox = self.lastMovedBox[:]
        for agent, action in enumerate(joint_action):
            if calc_results: 
                copy_literals = action.apply_effects(copy_literals)
            if isinstance(action, Move) and copy_lastMovedBox[agent] is not None:
                copy_recalculateDistanceOfBox[agent] = copy_lastMovedBox[agent]
                copy_lastMovedBox[agent] = None
            if isinstance(action, Push) or isinstance(action, Pull):
                copy_lastMovedBox[agent] = action.box
            
        copy_state = State(copy_literals)
        copy_state.parent = self
        copy_state.joint_action = joint_action[:]
        copy_state.g = self.g + 1
        copy_state.recalculateDistanceOfBox = copy_recalculateDistanceOfBox
        copy_state.lastMovedBox = copy_lastMovedBox

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
        joint_action: list[Action] = [Action(0) for _ in range(num_agents)]
        actions_permutation = [0] * num_agents
        expanded_states = []
        while True:
            for agent in range(num_agents):
                joint_action[agent] = applicable_actions[agent][
                    actions_permutation[agent]
                ]

            (check, result) = self.is_conflicting(joint_action)
            if not check:
                expanded_states.append(self.result(joint_action, result))

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

    @staticmethod
    def is_applicable(action: Action, literals: set[Atom]) -> bool:
        return action.check_preconditions(literals)

    def get_applicable_actions(self, agent: int) -> Action:
        agtfrom = self.agent_locations[agent]
        possibilities = []
        possible_actions = [Action, Move, Push, Pull]

        agtfrom_neighbours = Location.get_neighbours(agtfrom)
        for action in possible_actions:
            if action is Move:
                for agtto in agtfrom_neighbours:
                    action = Move(agent, agtfrom, agtto)
                    if self.is_applicable(action, self.literals):
                        possibilities.append(action)
            elif action is Push:
                for boxfrom in agtfrom_neighbours:
                    boxes = [
                        c
                        for c in State.agent_box_dict[agent]
                        if encode_atom_pos(AtomType.BOX_AT, boxfrom, c) in self.literals
                    ]
                    boxfrom_neighbours = Location.get_neighbours(boxfrom)
                    for box in boxes:
                        for boxto in boxfrom_neighbours:
                            action = Push(agent, agtfrom, box, boxfrom, boxto)
                            if self.is_applicable(action, self.literals):
                                possibilities.append(action)
            elif action is Pull:
                for boxfrom in agtfrom_neighbours:
                    boxes = [
                        c
                        for c in State.agent_box_dict[agent]
                        if encode_atom_pos(AtomType.BOX_AT, boxfrom, c) in self.literals
                    ]
                    for box in boxes:
                        for agtto in agtfrom_neighbours:
                            action = Pull(agent, agtfrom, agtto, box, boxfrom)
                            if self.is_applicable(action, self.literals):
                                possibilities.append(action)
            elif action is Action:
                possibilities.append(Action(agent))

        return possibilities

    def is_conflicting(self, joint_action: list[Action]) -> tuple[bool, set[Atom]]:
        # This follows the following logic:
        # For all applicable actions ai and aj where the precondition of one is inconsistent with the
        # effect of the other, either CellCon ict(ai aj) or BoxCon ict(ai aj) holds.
        literals = set(self.literals)

        for agt, action in enumerate(joint_action):
            if self.is_applicable(action, literals):
                literals = action.apply_effects(literals, True)
            else:
                return (True, None)

        return (False, literals)

    def extract_plan(self) -> list[list[Action]]:
        plan = [None] * self.g
        state = self

        while state.joint_action is not None:
            plan[state.g - 1] = state.joint_action
            state = state.parent

        return plan

    def __hash__(self):
        if self._hash is None:
            prime: int = 31
            _hash: int = 1
            _hash = _hash * prime + hash(tuple(self.literals))
            _hash = _hash * prime + hash(tuple(State.agent_colors))
            _hash = _hash * prime + hash(tuple(State.box_colors))
            _hash = _hash * prime + hash(tuple(State.goal_literals))
            self._hash = _hash
        return self._hash

    def __eq__(self, other):
        if self is other:
            return True

        if isinstance(other, State):
            return set(self.literals) == set(other.literals)

        return False

    def __repr__(self):
        return f"||{'^'.join(str(lit) for lit in self.literals)}||"
