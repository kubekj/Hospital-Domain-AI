from typing import Tuple

from src.cbs.agent import Agent


class Conflict:
    def __init__(self, agent_a: Agent, agent_b: Agent, vertex: Tuple[int, int], time: int):
        self.agent_a = agent_a
        self.agent_b = agent_b
        self.vertex = vertex
        self.time = time
