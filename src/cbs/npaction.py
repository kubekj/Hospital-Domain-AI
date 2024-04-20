from enum import Enum, unique


@unique
class NPActionType(Enum):
    NoOp = 0
    Move = 1
    Push = 2
    Pull = 3


@unique
class NPAction(Enum):
    #   List of possible actions. Each action has the following parameters,
    #    taken in order from left to right:
    #    1. The name of the action as a string. This is the string sent to the server
    #    when the action is executed. Note that for Pull and Push actions the syntax is
    #    "Push(X,Y)" and "Pull(X,Y)" with no spaces.
    #    2. Action type: NoOp, Move, Push or Pull
    #    3. agentRowDelta: the vertical displacement of the agent (-1,0,+1)
    #    4. agentColDelta: the horizontal displacement of the agent (-1,0,+1)
    #    5. boxRowDelta: the vertical displacement of the box (-1,0,+1)
    #    6. boxColDelta: the horizontal displacement of the box (-1,0,+1)
    #    Note: Origo (0,0) is in the upper left corner. So +1 in the vertical direction is down (S)
    #    and +1 in the horizontal direction is right (E).
    NoOp = ("NoOp", NPActionType.NoOp, 0, 0, 0, 0)

    MoveN = ("Move(N)", NPActionType.Move, -1, 0, 0, 0)
    MoveS = ("Move(S)", NPActionType.Move, 1, 0, 0, 0)
    MoveE = ("Move(E)", NPActionType.Move, 0, 1, 0, 0)
    MoveW = ("Move(W)", NPActionType.Move, 0, -1, 0, 0)

    PushNN = ("Push(N,N)", NPActionType.Push, -1, 0, -1, 0)
    PushSS = ("Push(S,S)", NPActionType.Push, 1, 0, 1, 0)
    PushEE = ("Push(E,E)", NPActionType.Push, 0, 1, 0, 1)
    PushWW = ("Push(W,W)", NPActionType.Push, 0, -1, 0, -1)
    PushNE = ("Push(N,E)", NPActionType.Push, -1, 0, 0, 1)
    PushSE = ("Push(S,E)", NPActionType.Push, 1, 0, 0, 1)
    PushSW = ("Push(S,W)", NPActionType.Push, 1, 0, 0, -1)
    PushNW = ("Push(N,W)", NPActionType.Push, -1, 0, 0, -1)
    PushWN = ("Push(W,N)", NPActionType.Push, 0, -1, -1, 0)
    PushEN = ("Push(E,N)", NPActionType.Push, 0, 1, -1, 0)
    PushWS = ("Push(W,S)", NPActionType.Push, 0, -1, 1, 0)
    PushES = ("Push(E,S)", NPActionType.Push, 0, 1, 1, 0)

    PullNN = ("Pull(N,N)", NPActionType.Pull, -1, 0, -1, 0)
    PullSS = ("Pull(S,S)", NPActionType.Pull, 1, 0, 1, 0)
    PullEE = ("Pull(E,E)", NPActionType.Pull, 0, 1, 0, 1)
    PullWW = ("Pull(W,W)", NPActionType.Pull, 0, -1, 0, -1)
    PullNE = ("Pull(N,E)", NPActionType.Pull, -1, 0, 0, 1)
    PullSE = ("Pull(S,E)", NPActionType.Pull, 1, 0, 0, 1)
    PullSW = ("Pull(S,W)", NPActionType.Pull, 1, 0, 0, -1)
    PullNW = ("Pull(N,W)", NPActionType.Pull, -1, 0, 0, -1)
    PullWN = ("Pull(W,N)", NPActionType.Pull, 0, -1, -1, 0)
    PullEN = ("Pull(E,N)", NPActionType.Pull, 0, 1, -1, 0)
    PullWS = ("Pull(W,S)", NPActionType.Pull, 0, -1, 1, 0)
    PullES = ("Pull(E,S)", NPActionType.Pull, 0, 1, 1, 0)

    def __init__(self, name, action_type, ard, acd, brd, bcd):
        self.name_ = name
        self.action_type = action_type
        self.agent_row_delta = ard
        self.agent_col_delta = acd
        self.box_row_delta = brd
        self.box_col_delta = bcd
