from atom import AgentAt, Atom, Neighbour, Free, Location
from enum import Enum, unique


class Action:
    def __init__(self, agt: int):
        self.agt = agt

    def check_preconditions(self, literals: list[Atom]):
        return True

    def apply_effects(self, literals: list[Atom]):
        return literals

    def get_name(self):
        return "NoOp"


class Move(Action):
    def __init__(self, agt: int, agtfrom: Location, agtto: Location):
        super().__init__(agt)
        self.agtfrom = agtfrom
        self.agtto = agtto

    def check_preconditions(self, literals: list[Atom]):
        """
        Check if the preconditions of the Move action are satisfied in the given state.
        Preconditions:
        - AgentAt(agt, agtfrom)
        - Neighbour(agtfrom, agtto)
        - Free(agtto)
        """
        return (AgentAt(self.agt, self.agtfrom) in literals and
                Neighbour(self.agtfrom, self.agtto).eval()
                and Free(self.agtto).eval(literals)
                # and Free(self.agtto) in literals
                )

    def apply_effects(self, literals: list[Atom]):
        """
        Apply the effects of the Move action to the given state.
        Effects:
        - Remove AgentAt(agt, agtfrom)
        - Add AgentAt(agt, agtto)
        - Free(agtfrom)
        - Not Free(agtto)
        """
        if self.check_preconditions(literals):
            # ~AgentAt(agt,agtfrom)
            literals.remove(AgentAt(self.agt, self.agtfrom))
            # AgentAt(agt,agtto)
            literals.append(AgentAt(self.agt, self.agtto))
            # ~Free(agtto)
            # literals.remove(Free(self.agtto))
            # Free(agtfrom)
            # literals.append(Free(self.agtfrom))
            return literals
        else:
            raise Exception("Preconditions not satisfied for the Move action.")

    def get_name(self):
        if self.agtfrom.row != self.agtto.row and self.agtfrom.col != self.agtto.col:
            raise Exception("Move action is not possible")
        if self.agtfrom.row < self.agtto.row:
            return "Move(S)"
        elif self.agtfrom.row > self.agtto.row:
            return "Move(N)"
        elif self.agtfrom.col < self.agtto.col:
            return "Move(E)"
        elif self.agtfrom.col > self.agtto.col:
            return "Move(W)"
        return "NoOp"


@unique
class PossibleAction(Enum):
    NoOp = ("NoOp", Action, 0, 0, 0, 0)

    MoveN = ("Move(N)", Move, -1, 0, 0, 0)
    MoveS = ("Move(S)", Move, 1, 0, 0, 0)
    MoveE = ("Move(E)", Move, 0, 1, 0, 0)
    MoveW = ("Move(W)", Move, 0, -1, 0, 0)
