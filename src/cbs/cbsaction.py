from enum import Enum, unique


@unique
class CBSActionType(Enum):
    NoOp = 0
    Move = 1
    Push = 2
    Pull = 3


@unique
class CBSAction(Enum):
    """
    List of possible actions. Each action has the following parameters, taken in order from left to right:
        1. The name of the action as a string. This is the string sent to the server when the action is executed.
        Note that for Pull and Push actions the syntax is "Push(X,Y)" and "Pull(X,Y)" with no spaces.
        2. Action type: NoOp, Move, Push or Pull
        3. agentRowDelta: the vertical displacement of the agent (-1,0,+1)
        4. agentColDelta: the horizontal displacement of the agent (-1,0,+1)
        5. boxRowDelta: the vertical displacement of the box (-1,0,+1)
        6. boxColDelta: the horizontal displacement of the box (-1,0,+1)
    Note: Origo (0,0) is in the upper left corner.
    So +1 in the vertical direction is down (S) and +1 in the horizontal direction is right (E).
   """
    NoOp = ("NoOp", CBSActionType.NoOp, 0, 0, 0, 0)

    MoveN = ("Move(N)", CBSActionType.Move, -1, 0, 0, 0)
    MoveS = ("Move(S)", CBSActionType.Move, 1, 0, 0, 0)
    MoveE = ("Move(E)", CBSActionType.Move, 0, 1, 0, 0)
    MoveW = ("Move(W)", CBSActionType.Move, 0, -1, 0, 0)

    PushNN = ("Push(N,N)", CBSActionType.Push, -1, 0, -1, 0)
    PushSS = ("Push(S,S)", CBSActionType.Push, 1, 0, 1, 0)
    PushEE = ("Push(E,E)", CBSActionType.Push, 0, 1, 0, 1)
    PushWW = ("Push(W,W)", CBSActionType.Push, 0, -1, 0, -1)
    PushNE = ("Push(N,E)", CBSActionType.Push, -1, 0, 0, 1)
    PushSE = ("Push(S,E)", CBSActionType.Push, 1, 0, 0, 1)
    PushSW = ("Push(S,W)", CBSActionType.Push, 1, 0, 0, -1)
    PushNW = ("Push(N,W)", CBSActionType.Push, -1, 0, 0, -1)
    PushWN = ("Push(W,N)", CBSActionType.Push, 0, -1, -1, 0)
    PushEN = ("Push(E,N)", CBSActionType.Push, 0, 1, -1, 0)
    PushWS = ("Push(W,S)", CBSActionType.Push, 0, -1, 1, 0)
    PushES = ("Push(E,S)", CBSActionType.Push, 0, 1, 1, 0)

    PullNN = ("Pull(N,N)", CBSActionType.Pull, -1, 0, -1, 0)
    PullSS = ("Pull(S,S)", CBSActionType.Pull, 1, 0, 1, 0)
    PullEE = ("Pull(E,E)", CBSActionType.Pull, 0, 1, 0, 1)
    PullWW = ("Pull(W,W)", CBSActionType.Pull, 0, -1, 0, -1)
    PullNE = ("Pull(N,E)", CBSActionType.Pull, -1, 0, 0, 1)
    PullSE = ("Pull(S,E)", CBSActionType.Pull, 1, 0, 0, 1)
    PullSW = ("Pull(S,W)", CBSActionType.Pull, 1, 0, 0, -1)
    PullNW = ("Pull(N,W)", CBSActionType.Pull, -1, 0, 0, -1)
    PullWN = ("Pull(W,N)", CBSActionType.Pull, 0, -1, -1, 0)
    PullEN = ("Pull(E,N)", CBSActionType.Pull, 0, 1, -1, 0)
    PullWS = ("Pull(W,S)", CBSActionType.Pull, 0, -1, 1, 0)
    PullES = ("Pull(E,S)", CBSActionType.Pull, 0, 1, 1, 0)

    def __init__(self, name, action_type, ard, acd, brd, bcd):
        self.name_ = name
        self.action_type = action_type
        self.agent_row_delta = ard
        self.agent_col_delta = acd
        self.box_row_delta = brd
        self.box_col_delta = bcd
