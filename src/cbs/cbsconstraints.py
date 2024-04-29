from src.cbs.cbsagent import CBSAgent
from typing import Dict, Tuple, Set
from copy import deepcopy

class CBSConstraints:
    def __init__(self):
        #                                   time,         obstacles
        self.agent_constraints: Dict[CBSAgent: Dict[int, Set[Tuple[int, int]]]] = dict()

    def fork(self, agent: CBSAgent, obstacle: Tuple[int, int], start: int, end: int) -> 'CBSConstraints':
        """
        Deepcopy self with additional constraints
        """
        new_constraints = deepcopy(self)
        for time in range(start, end):
            new_constraints.agent_constraints.setdefault(agent, {}).setdefault(time, set()).add(obstacle)
        return new_constraints

    def setdefault(self, key, default):
        return self.agent_constraints.setdefault(key, default)

    def __getitem__(self, agent):
        return self.agent_constraints[agent]

    def __iter__(self):
        for key in self.agent_constraints:
            yield key

    def __str__(self):
        return str(self.agent_constraints)
