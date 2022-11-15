"""
Tic Tac Toe Player
"""

import math
from copy import deepcopy
from random import randint

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    xs = 0
    os = 0
    for bo in board:
        for b in bo:
            if b == X:
                xs = xs + 1
            elif b == O:
                os = os + 1
    
    if xs > os:
        return O
    elif not terminal(board) and xs == os:
        return X
    else:
        return None


    raise NotImplementedError


def actions(board):

    """
    Returns set of all possible actions (i, j) available on the board.
    """
    moves = set()

    for r, row in enumerate(board):
        for j, ji in enumerate(row):
            if ji == None:
                moves.add((r, j))

    return moves

    raise NotImplementedError


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    p = player(board)
    new = deepcopy(board)
    i, j = action

    if board[i][j] == None:
        new[i][j] = p
    else:
        raise Exception

    return new
    

    raise NotImplementedError


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    def winnery(board):
        #Check for winner in y direction
        w = None
        for i in range(len(board)):
            w = board[0][i]
            for j in range(len(board)):
                if board[j][i] != w:
                    w = None
            if w:
                return w
        return w

    def winnerx(board):
        #Check for winner in x direction
        w = None
        for i in range(len(board)):
            w = board[i][0]
            for j in range(len(board)):
                if board[i][j] != w:
                    w = None
            if w:
                return w
        return w


    def winnerdiag(board):
        #Check for winner in diagonally
        w = None
        w = board[0][0]
        for i in range(len(board)):
            if board[i][i] != w:
                w = None
        if w:
            return w

        w = board[0][len(board) - 1]
        for i in range(len(board)):
            j = len(board) - 1 - i
            if board[i][j] != w:
                w = None

        return w

    win = winnerx(board) or winnery(board) or winnerdiag(board) or None
    return win

    raise NotImplementedError


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) != None:
        return True

    for i in board:
        for j in i:
            if j == EMPTY:
                return False
    return True


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """

    if winner(board) is not None:
        return True
    elif len(actions(board)) == 0:
        return True
    return False

    raise NotImplementedError


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """

    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    return 0

    raise NotImplementedError


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    pl = player(board)

    if terminal(board):
        return None
    
    if board == initial_state():
        return (randint(0,2), randint(0,2))
    
    if pl == X:
        v = -100
        best = None
        for action in actions(board):
            # get optimal action for X
            minresult = minvalue(result(board, action))
            if minresult > v:
                v = minresult
                best = action

    elif pl == O:
        v = 100
        best = None
        #get optimal action for O
        for action in actions(board):
            maxresult = maxvalue(result(board, action))
            if maxresult < v:
                v = maxresult
                best = action

    return best

    raise NotImplementedError

def maxvalue(board):
    if terminal(board):
        return utility(board)
    v = -100
    for action in actions(board):
        v = max(v, minvalue(result(board, action)))
    return v

def minvalue(board):
    if terminal(board): 
        return utility(board)
    v = 100
    for action in actions(board):
        v = min(v, maxvalue(result(board, action)))
    return v