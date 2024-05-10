from enum import Enum, unique
from src.domain.atom import *


class Action:
    def __init__(self, agt: int):
        self.agt = agt

    def __repr__(self) -> str:
        return f"Action({self.agt})"

    def check_preconditions(self, literals: LiteralList):
        return True

    def apply_effects(self, literals: LiteralList, skip_check = False):
        return literals

    def get_name(self):
        return "NoOp"


class Move(Action):
    def __init__(self, agt: int, agtfrom: Pos, agtto: Pos):
        super().__init__(agt)
        self.agtfrom = agtfrom
        self.agtto = agtto

    def __repr__(self) -> str:
        fr,fc = self.agtfrom
        tr,tc = self.agtto
        return f"Move({self.agt}, {(fr,fc)}, {(tr,tc)})"

    def check_preconditions(self, literals: LiteralList):
        """
        Check if the preconditions of the Move action are satisfied in the given state.
        Preconditions:
        - AgentAt(agt, agtfrom)
        - Neighbour(agtfrom, agtto)
        - Free(agtto)
        """
        return (
            encode_agent(self.agtfrom, self.agt) in literals[AtomType.AGENT_AT]
            and eval_neighbour(self.agtfrom, self.agtto)
            and eval_free(self.agtto, literals)
            # and Free(self.agtto) in literals
        )

    def apply_effects(self, literals: LiteralList, skip_check = False):
        """
        Apply the effects of the Move action to the given state.
        Effects:
        - Remove AgentAt(agt, agtfrom)
        - Add AgentAt(agt, agtto)
        - Free(agtfrom)
        - Not Free(agtto)
        """
        if skip_check or self.check_preconditions(literals):
            old = encode_agent(self.agtfrom, self.agt)
            new = encode_agent(self.agtto, self.agt)

            # ~AgentAt(agt,agtfrom)
            literals[AtomType.AGENT_AT].remove(old)
            # AgentAt(agt,agtto)
            literals[AtomType.AGENT_AT].add(new)
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
        self, agt: int, agtfrom: Pos, box: Box, boxfrom: Pos, boxto: Pos
    ):
        super().__init__(agt)
        self.box = box
        self.agtfrom = agtfrom
        self.boxfrom = boxfrom
        self.boxto = boxto

    def __repr__(self) -> str:
        afr,afc = self.agtfrom
        bfr,bfc = self.boxfrom
        btr,btc = self.boxto
        return f"Push({self.agt}, {(afr,afc)}, {chr(self.box[0] + ord("A")),self.box[1]}, {(bfr,bfc)}, {(btr,btc)})"

    def check_preconditions(self, literals: LiteralList):
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
            encode_agent(self.agtfrom, self.agt) in literals[AtomType.AGENT_AT] #Agent_at
            and encode_box(self.boxfrom, self.box) in literals[AtomType.BOX_AT] #Box_at
            and eval_neighbour(self.agtfrom, self.boxfrom)
            and eval_neighbour(self.boxfrom, self.boxto)
            and eval_free(self.boxto, literals)
            and self.agtfrom != self.boxto
        )

    def apply_effects(self, literals: LiteralList, skip_check = False):
        """
        Apply the effects of the Move action to the given state.
        Effects:
        - Remove AgentAt(agt, agtfrom)
        - Add AgentAt(agt, boxfrom)
        - Free(agtfrom)
        - Not Free(boxfrom)
        """
        if skip_check or self.check_preconditions(literals):
            agtgfrom = encode_agent(self.agtfrom, self.agt)
            agtgto = encode_agent(self.boxfrom, self.agt)
            boxfrom = encode_box(self.boxfrom, self.box)
            boxto = encode_box(self.boxto, self.box)

            # ~AgentAt(agt,agtfrom)
            literals[AtomType.AGENT_AT].remove(agtgfrom)
            # AgentAt(agt,boxfrom)
            literals[AtomType.AGENT_AT].add(agtgto)
            # ~BoxAt(box,boxfrom)
            literals[AtomType.BOX_AT].remove(boxfrom)
            # BoxAt(box,boxto)
            literals[AtomType.BOX_AT].add(boxto)
            return literals
        else:
            raise Exception("Preconditions not satisfied for the Move action.")

    def get_name(self):
        agtfrom_row, agtfrom_col = self.agtfrom
        boxfrom_row, boxfrom_col = self.boxfrom
        boxto_row, boxto_col = self.boxto

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
        self, agt: int, agtfrom: Pos, agtto: Pos, box: Box, boxfrom: Pos
    ):
        super().__init__(agt)
        self.box = box
        self.agtto = agtto
        self.agtfrom = agtfrom
        self.boxfrom = boxfrom

    def __repr__(self) -> str:
        atr,atc = self.agtto
        afr,afc = self.agtfrom
        bfr,bfc = self.boxfrom
        return f"Pull({self.agt}, {(afr,afc)}, {(atr,atc)}, {chr(self.box[0] + ord("A")),self.box[1]}, {(bfr,bfc)})"

    def check_preconditions(self, literals: LiteralList):
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
            encode_agent(self.agtfrom, self.agt) in literals[AtomType.AGENT_AT] #Agent_at
            and eval_neighbour(self.agtfrom, self.agtto)
            and eval_neighbour(self.agtfrom, self.boxfrom)
            and encode_box(self.boxfrom, self.box) in literals[AtomType.BOX_AT] #Box_at
            and eval_free(self.agtto, literals)
            and self.agtto != self.agtfrom
        )

    def apply_effects(self, literals: LiteralList, skip_check = False):
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
            agtto = encode_agent(self.agtto, self.agt)
            agtfrom = encode_agent(self.agtfrom, self.agt)
            boxfrom = encode_box(self.boxfrom, self.box)
            boxto = encode_box(self.agtfrom, self.box)

            # ~AgentAt(agt,agtfrom)
            literals[AtomType.AGENT_AT].remove(agtfrom)
            # AgentAt(agt,agtto)
            literals[AtomType.AGENT_AT].add(agtto)
            # ~BoxAt(box,boxfrom)
            literals[AtomType.BOX_AT].remove(boxfrom)
            # BoxAt(box,boxto)
            literals[AtomType.BOX_AT].add(boxto)
            return literals
        else:
            raise Exception("Preconditions not satisfied for the Move action.")

    def get_name(self):
        agtto_row, agtto_col = self.agtto
        agtfrom_row, agtfrom_col = self.agtfrom
        boxfrom_row, boxfrom_col = self.boxfrom

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
