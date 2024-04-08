from enum import Enum, unique
from src.domain.atom import Atom, BoxAt, Location, AgentAt, Neighbour, Free


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
        return (
            AgentAt(self.agt, self.agtfrom) in literals
            and Neighbour(self.agtfrom, self.agtto).eval()
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


class Push(Action):
    def __init__(
        self, agt: int, agtfrom: Location, box: int, boxfrom: Location, boxto: Location
    ):
        super().__init__(agt)
        self.agtfrom = agtfrom
        self.box = box
        self.boxfrom = boxfrom
        self.boxto = boxto

    def check_preconditions(self, literals: list[Atom]):
        """
        Check if the preconditions of the Move action are satisfied in the given state.
        Preconditions:
        - AgentAt(agt, agtfrom)
        - Neighbour(agtfrom, boxfrom)
        - Neighbour(boxfrom, boxto)
        - BoxAt(box, boxfrom)
        - Free(agtto)
        """
        return (
            AgentAt(self.agt, self.agtfrom) in literals
            and Neighbour(self.agtfrom, self.boxfrom).eval()
            and Neighbour(self.boxfrom, self.boxto).eval()
            and BoxAt(self.box, self.boxfrom) in literals
            and Free(self.boxto).eval(literals)
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
            literals.append(AgentAt(self.agt, self.boxfrom))
            # ~BoxAt(box,boxfrom)
            literals.remove(BoxAt(self.box, self.boxfrom))
            # BoxAt(box,boxto)
            literals.append(BoxAt(self.box, self.boxto))
            return literals
        else:
            raise Exception("Preconditions not satisfied for the Move action.")

    def get_name(self):
        if (
            self.agtfrom.row != self.boxfrom.row
            and self.agtfrom.col != self.boxfrom.col
        ):
            raise Exception("Move action is not possible")
        agentMove = None
        if self.agtfrom.row < self.boxfrom.row:
            agentMove = "S"
        elif self.agtfrom.row > self.boxfrom.row:
            agentMove = "N"
        elif self.agtfrom.col < self.boxfrom.col:
            agentMove = "E"
        elif self.agtfrom.col > self.boxfrom.col:
            agentMove = "W"

        boxMove = None
        if self.boxfrom.row < self.boxto.row:
            boxMove = "S"
        elif self.boxfrom.row > self.boxto.row:
            boxMove = "N"
        elif self.boxfrom.col < self.boxto.col:
            boxMove = "E"
        elif self.boxfrom.col > self.boxto.col:
            boxMove = "W"

        if agentMove is None or boxMove is None:
            return "NoOp"
        else:
            print(agentMove, boxMove)
            return f"Push({agentMove},{boxMove})"


class Pull(Action):
    def __init__(
        self, agt: int, agtfrom: Location, agtto: Location, box: int, boxfrom: Location
    ):
        super().__init__(agt)
        self.agtfrom = agtfrom
        self.agtto = agtto
        self.box = box
        self.boxfrom = boxfrom

    def check_preconditions(self, literals: list[Atom]):
        """
        Check if the preconditions of the Move action are satisfied in the given state.
        Preconditions:
        - AgentAt(agt, agtfrom)
        - Neighbour(agtfrom, agtto)
        - Neighbour(agtfrom, boxfrom)
        - BoxAt(box, boxfrom)
        - Free(agtto)
        """
        return (
            AgentAt(self.agt, self.agtfrom) in literals
            and Neighbour(self.agtfrom, self.agtto).eval()
            and Neighbour(self.agtfrom, self.boxfrom).eval()
            and BoxAt(self.box, self.boxfrom) in literals
            and Free(self.agtto).eval(literals)
        )

    def apply_effects(self, literals: list[Atom]):
        """
        Apply the effects of the Move action to the given state.
        Effects:
        - Remove AgentAt(agt, agtfrom)
        - Add AgentAt(agt, agtto)
        - Remove BoxAt(box, boxfrom)
        - Add BoxAt(box, agtfrom)
        - Free(boxfrom)
        - Not Free(agtto)
        """
        if self.check_preconditions(literals):
            # ~AgentAt(agt,agtfrom)
            literals.remove(AgentAt(self.agt, self.agtfrom))
            # AgentAt(agt,agtto)
            literals.append(AgentAt(self.agt, self.agtto))
            # ~BoxAt(box,boxfrom)
            literals.remove(BoxAt(self.box, self.boxfrom))
            # BoxAt(box,boxto)
            literals.append(BoxAt(self.box, self.agtfrom))
            return literals
        else:
            raise Exception("Preconditions not satisfied for the Move action.")

    def get_name(self):
        if self.agtfrom.row != self.agtto.row and self.agtfrom.col != self.agtto.col:
            raise Exception("Move action is not possible")
        agentMove = None
        if self.agtfrom.row < self.boxfrom.row:
            agentMove = "N"
        elif self.agtfrom.row > self.boxfrom.row:
            agentMove = "S"
        elif self.agtfrom.col < self.boxfrom.col:
            agentMove = "W"
        elif self.agtfrom.col > self.boxfrom.col:
            agentMove = "E"

        boxMove = None
        if self.boxfrom.row < self.agtfrom.row:
            boxMove = "N"
        elif self.boxfrom.row > self.agtfrom.row:
            boxMove = "S"
        elif self.boxfrom.col < self.agtfrom.col:
            boxMove = "W"
        elif self.boxfrom.col > self.agtfrom.col:
            boxMove = "E"
        if agentMove is None or boxMove is None:
            return "NoOp"
        else:
            return f"Pull({agentMove},{boxMove})"


@unique
class PossibleAction(Enum):
    NoOp = ("NoOp", Action, 0, 0, 0, 0)

    MoveN = ("Move(N)", Move, -1, 0, 0, 0)
    MoveS = ("Move(S)", Move, 1, 0, 0, 0)
    MoveE = ("Move(E)", Move, 0, 1, 0, 0)
    MoveW = ("Move(W)", Move, 0, -1, 0, 0)

    PushNN = ("Push(N,N)", Push, -1, 0, -1, 0)
    PushSS = ("Push(S,S)", Push, 1, 0, 1, 0)
    PushEE = ("Push(E,E)", Push, 0, 1, 0, 1)
    PushWW = ("Push(W,W)", Push, 0, -1, 0, -1)
    PushNE = ("Push(N,E)", Push, -1, 0, 0, 1)
    PushSE = ("Push(S,E)", Push, 1, 0, 0, 1)
    PushSW = ("Push(S,W)", Push, 1, 0, 0, -1)
    PushNW = ("Push(N,W)", Push, -1, 0, 0, -1)
    PushWN = ("Push(W,N)", Push, 0, -1, -1, 0)
    PushEN = ("Push(E,N)", Push, 0, 1, -1, 0)
    PushWS = ("Push(W,S)", Push, 0, -1, 1, 0)
    PushES = ("Push(E,S)", Push, 0, 1, 1, 0)

    PullNN = ("Pull(N,N)", Pull, -1, 0, -1, 0)
    PullSS = ("Pull(S,S)", Pull, 1, 0, 1, 0)
    PullEE = ("Pull(E,E)", Pull, 0, 1, 0, 1)
    PullWW = ("Pull(W,W)", Pull, 0, -1, 0, -1)
    PullNE = ("Pull(N,E)", Pull, -1, 0, 0, 1)
    PullSE = ("Pull(S,E)", Pull, 1, 0, 0, 1)
    PullSW = ("Pull(S,W)", Pull, 1, 0, 0, -1)
    PullNW = ("Pull(N,W)", Pull, -1, 0, 0, -1)
    PullWN = ("Pull(W,N)", Pull, 0, -1, -1, 0)
    PullEN = ("Pull(E,N)", Pull, 0, 1, -1, 0)
    PullWS = ("Pull(W,S)", Pull, 0, -1, 1, 0)
    PullES = ("Pull(E,S)", Pull, 0, 1, 1, 0)
