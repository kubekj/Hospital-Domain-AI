from enum import Enum, unique
from src.domain.atom import *


class Action:
    def __init__(self, agt: int):
        self.agt = agt

    def check_preconditions(self, literals: set[Atom]):
        return True

    def apply_effects(self, literals: set[Atom], skip_check = False):
        return literals

    def get_name(self):
        return "NoOp"


class Move(Action):
    def __init__(self, agt: int, agtfrom: Pos, agtto: Pos):
        super().__init__(agt)
        self.agtfrom = agtfrom
        self.agtto = agtto

    def check_preconditions(self, literals: set[Atom]):
        """
        Check if the preconditions of the Move action are satisfied in the given state.
        Preconditions:
        - AgentAt(agt, agtfrom)
        - Neighbour(agtfrom, agtto)
        - Free(agtto)
        """
        return (
            encode_atom_pos(AtomType.AGENT_AT, self.agtfrom, self.agt) in literals
            and eval_neighbour(self.agtfrom, self.agtto)
            and eval_free(self.agtto, literals)
            # and Free(self.agtto) in literals
        )

    def apply_effects(self, literals: set[Atom], skip_check = False):
        """
        Apply the effects of the Move action to the given state.
        Effects:
        - Remove AgentAt(agt, agtfrom)
        - Add AgentAt(agt, agtto)
        - Free(agtfrom)
        - Not Free(agtto)
        """
        if skip_check or self.check_preconditions(literals):
            old = encode_atom_pos(AtomType.AGENT_AT, self.agtfrom, self.agt)
            new = encode_atom_pos(AtomType.AGENT_AT, self.agtto, self.agt)

            # ~AgentAt(agt,agtfrom)
            literals.remove(old)
            # AgentAt(agt,agtto)
            literals.add(new)
            # ~Free(agtto)
            # Free(agtfrom)
            return literals
        else:
            raise Exception("Preconditions not satisfied for the Move action.")

    def get_name(self):
        agtfrom_row, agtfrom_col = self.agtfrom
        agtto_row, agtto_col = self.agtto

        if agtfrom_row != agtto_row and agtfrom_col != agtto_col:
            raise Exception("Move action is not possible")
        agentMove = None
        if agtfrom_row < agtto_row:
            agentMove = "S"
        elif agtfrom_row > agtto_row:
            agentMove = "N"
        elif agtfrom_col < agtto_col:
            agentMove = "E"
        elif agtfrom_col > agtto_col:
            agentMove = "W"

        if agentMove is None:
            return "NoOp"
        else:
            return f"Move({agentMove})"


class Push(Action):
    def __init__(
        self, agt: int, agtfrom: Pos, box: int, boxfrom: Pos, boxto: Pos
    ):
        super().__init__(agt)
        self.box = box
        self.agtfrom = encode_atom_pos(AtomType.AGENT_AT, agtfrom, agt)
        self.boxfrom = encode_atom_pos(AtomType.BOX_AT, boxfrom, box)
        self.boxto = encode_atom_pos(AtomType.BOX_AT, boxto, box)

    def check_preconditions(self, literals: set[Atom]):
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
            self.agtfrom in literals #Agent_at
            and self.boxfrom in literals #Box_at
            and eval_neighbour(self.agtfrom, self.boxfrom)
            and eval_neighbour(self.boxfrom, self.boxto)
            and eval_free(self.boxto, literals)
            and self.agtfrom != self.boxto
        )

    def apply_effects(self, literals: set[Atom], skip_check = False):
        """
        Apply the effects of the Move action to the given state.
        Effects:
        - Remove AgentAt(agt, agtfrom)
        - Add AgentAt(agt, boxfrom)
        - Free(agtfrom)
        - Not Free(boxfrom)
        """
        if skip_check or self.check_preconditions(literals):
            # ~AgentAt(agt,agtfrom)
            literals.remove(self.agtfrom)
            # AgentAt(agt,boxfrom)
            literals.add(self.boxfrom)
            # ~BoxAt(box,boxfrom)
            literals.remove(self.boxfrom)
            # BoxAt(box,boxto)
            literals.add(self.boxto)
            return literals
        else:
            raise Exception("Preconditions not satisfied for the Move action.")

    def get_name(self):
        agtfrom_row, agtfrom_col = get_atom_location(self.agtfrom)
        boxfrom_row, boxfrom_col = get_atom_location(self.boxfrom)
        boxto_row, boxto_col = get_atom_location(self.boxto)

        if agtfrom_row == boxfrom_row and agtfrom_col == boxfrom_col:
            raise Exception("Move action is not possible")
        
        agentMove = None
        if agtfrom_row < boxfrom_row:
            agentMove = "S"
        elif agtfrom_row > boxfrom_row:
            agentMove = "N"
        elif agtfrom_col < boxfrom_col:
            agentMove = "E"
        elif agtfrom_col > boxfrom_col:
            agentMove = "W"

        boxMove = None
        if boxfrom_row < boxto_row:
            boxMove = "S"
        elif boxfrom_row > boxto_row:
            boxMove = "N"
        elif boxfrom_col < boxto_col:
            boxMove = "E"
        elif boxfrom_col > boxto_col:
            boxMove = "W"

        if agentMove is None or boxMove is None:
            return "NoOp"
        else:
            return f"Push({agentMove},{boxMove})"



class Pull(Action):
    def __init__(
        self, agt: int, agtfrom: Pos, agtto: Pos, box: int, boxfrom: Pos
    ):
        super().__init__(agt)
        self.box = box
        self.agtto = encode_atom_pos(AtomType.AGENT_AT, agtto, agt)
        self.agtfrom = encode_atom_pos(AtomType.AGENT_AT, agtfrom, agt)
        self.boxfrom = encode_atom_pos(AtomType.BOX_AT, boxfrom, box)

    def check_preconditions(self, literals: set[Atom]):
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
            self.agtfrom in literals #Agent_at
            and eval_neighbour(self.agtfrom, self.agtto)
            and eval_neighbour(self.agtfrom, self.boxfrom)
            and self.boxfrom in literals #Box_at
            and eval_free(self.agtto, literals)
            and self.agtto != self.agtfrom
        )

    def apply_effects(self, literals: set[Atom], skip_check = False):
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
        if skip_check or self.check_preconditions(literals):
            # ~AgentAt(agt,agtfrom)
            literals.remove(self.agtfrom)
            # AgentAt(agt,agtto)
            literals.add(self.agtto)
            # ~BoxAt(box,boxfrom)
            literals.remove(self.boxfrom)
            # BoxAt(box,boxto)
            literals.add(self.agtfrom)
            return literals
        else:
            raise Exception("Preconditions not satisfied for the Move action.")

    def get_name(self):
        agtto_row, agtto_col = get_atom_location(self.agtto)
        agtfrom_row, agtfrom_col = get_atom_location(self.agtfrom)
        boxfrom_row, boxfrom_col = get_atom_location(self.boxfrom)

        if agtfrom_row != agtto_row and agtfrom_col != agtto_col:
            raise Exception("Move action is not possible")
        agentMove = None
        if agtfrom_row < agtto_row:
            agentMove = "S"
        elif agtfrom_row > agtto_row:
            agentMove = "N"
        elif agtfrom_col < agtto_col:
            agentMove = "E"
        elif agtfrom_col > agtto_col:
            agentMove = "W"

        boxMove = None
        if boxfrom_row < agtfrom_row:
            boxMove = "S"
        elif boxfrom_row > agtfrom_row:
            boxMove = "N"
        elif boxfrom_col < agtfrom_col:
            boxMove = "E"
        elif boxfrom_col > agtfrom_col:
            boxMove = "W"
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
