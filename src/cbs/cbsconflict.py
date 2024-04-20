from typing import Tuple

from src.cbs.cbsagent import CBSAgent


class CBSConflict:
    def __init__(self, agent_a: CBSAgent, agent_b: CBSAgent, vertex: Tuple[int, int], time: int):
        self.agent_a = agent_a
        self.agent_b = agent_b
        self.vertex = vertex
        self.time = time
