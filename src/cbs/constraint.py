from typing import Tuple

from src.cbs.agent import Agent

from enum import Enum, auto

class ConstraintType(Enum):
    VERTEX = auto()
    EDGE = auto()

class Constraint:
    def __init__(self, agent: Agent, vertex: Tuple[int, int], time: int, constraint_type: ConstraintType):
        """
        Initialize a new constraint for the CBS algorithm.

        :param agent: The agent to which this constraint applies.
        :param vertex: The grid position (x, y) that is subject to the constraint.
        :param time: The specific time step at which the constraint applies.
        :param constraint_type: The type of constraint ('vertex' for specific position blocking,
                                'edge' for transition blocking between two vertices).
        """
        self.agent = agent
        self.vertex = vertex
        self.time = time
        self.constraint_type = constraint_type

    def __str__(self):
        return f"Constraint(agent={self.agent}, vertex={self.vertex}, time={self.time}, type={self.constraint_type.name})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return (self.agent == other.agent and self.vertex == other.vertex and
                self.time == other.time and self.constraint_type == other.constraint_type)

    def __hash__(self):
        return hash((self.agent, self.vertex, self.time, self.constraint_type))
