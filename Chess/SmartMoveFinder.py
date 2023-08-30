import random

PIECE_SCORE = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}

KNIGHT_SCORES = [[1,1,1,1,1,1,1,1],
                 [1,2,2,2,2,2,2,1],
                 [1,2,3,3,3,3,2,1],
                 [1,2,3,4,4,3,2,1],
                 [1,2,3,4,4,3,2,1],
                 [1,2,3,3,3,3,2,1],
                 [1,2,2,2,2,2,2,1],
                 [1,1,1,1,1,1,1,1]]

BISHOP_SCORES = [[4,3,2,1,1,2,3,4],
                 [3,4,3,2,2,3,4,3],
                 [2,3,4,3,3,4,3,2],
                 [1,2,3,4,4,3,2,1],
                 [1,2,3,4,4,3,2,1],
                 [2,3,4,3,3,4,3,2],
                 [3,4,3,2,2,3,4,3],
                 [4,3,2,1,1,2,3,4]]

ROOK_SCORES = [[4,3,4,4,4,4,3,4],
               [4,4,4,4,4,4,4,4],
               [1,1,2,3,3,2,1,1],
               [1,2,3,4,4,3,2,1],
               [1,2,3,4,4,3,2,1],
               [1,1,2,2,2,2,1,1],
               [4,4,4,4,4,4,4,4],
               [4,3,4,4,4,4,3,4]]

QUEEN_SCORES = [[1,1,1,3,1,1,1,1],
                [1,2,3,3,3,1,1,1],
                [1,4,3,3,3,4,2,1],
                [1,2,3,3,3,2,2,1],
                [1,2,3,3,3,2,2,1],
                [1,4,3,3,3,4,2,1],
                [1,1,2,3,3,1,1,1],
                [1,1,1,3,1,1,1,1]]

WHITE_PAWN_SCORES = [[8,8,8,8,8,8,8,8],
               [8,8,8,8,8,8,8,8],
               [5,6,6,7,7,6,6,5],
               [2,3,3,5,5,3,3,2],
               [1,2,3,4,4,3,2,1],
               [1,1,2,3,3,2,1,1],
               [1,1,1,0,0,1,1,1],
               [0,0,0,0,0,0,0,0]]

BLACK_PAWN_SCORES = [[0,0,0,0,0,0,0,0],
                [1,1,1,0,0,1,1,1],
                [1,1,2,3,3,2,1,1],
                [1,2,3,4,4,3,2,1],
                [2,3,3,5,5,3,3,2],
                [5,6,6,7,7,6,6,5],
                [8,8,8,8,8,8,8,8],
                [8,8,8,8,8,8,8,8]]

PIECE_POSITION_SCORES = {
    "wp": WHITE_PAWN_SCORES,
    "bp": BLACK_PAWN_SCORES,
    "wN": KNIGHT_SCORES,
    "bN": KNIGHT_SCORES[::-1],
    "wB": BISHOP_SCORES,
    "bB": BISHOP_SCORES[::-1],
    "wR": ROOK_SCORES,
    "bR": ROOK_SCORES[::-1],
    "wQ": QUEEN_SCORES,
    "bQ": QUEEN_SCORES[::-1]
}

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3
nextMove = None

"""
Picks and returns a random move
"""
def findRandomMove(validMoves):
    return random.choice(validMoves)


def getScore(gs, validMoves):
    random.shuffle(validMoves)
    bestScore = findMoveNegaMaxAlphaBeta(gs, validMoves, 1, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)/2
    return bestScore
"""
Find nega max move helper. First recursive caller
"""
def findBestMove(gs, validMoves, returnQueue, depth):
    global nextMove
    nextMove = None
    DEPTH=depth
    random.shuffle(validMoves)
    findMoveNegaMaxAlphaBeta(gs, validMoves, depth, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    returnQueue.put(nextMove)

def getBestMove(gs, validMoves, returnQueue):
    global nextMove
    nextMove = None
    DEPTH=1
    random.shuffle(validMoves)
    findMoveNegaMaxAlphaBeta(gs, validMoves, 1, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    returnQueue.put(nextMove)


"""
White searches the highest value, black the lowest
Explanation: https://www.youtube.com/watch?v=l-hh51ncgDI
"""
def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
    if depth==0:
        return turnMultiplier*scoreBoard(gs)
    maxScore=-CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves=gs.getValidMoves()
        score=-findMoveNegaMaxAlphaBeta(gs,nextMoves,depth-1,-beta,-alpha,-turnMultiplier)
        if score>maxScore:
            maxScore=score
            if depth==DEPTH:
                nextMove=move
        gs.undoMove()
        if maxScore>alpha:
            alpha=maxScore
        if alpha>=beta:
            break
    return maxScore


"""
A positive score is good for white, a negative score is good for black
"""
def scoreBoard(gs):
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.stalemate:
        return STALEMATE

    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            piece = gs.board[row][col]
            if piece != "--":
                # score it by position
                piecePositionScore = 0
                if piece[1] != "K":
                    piecePositionScore = PIECE_POSITION_SCORES[piece][row][col]

                # score it by material
                if piece[0] == 'w':
                    score += PIECE_SCORE[piece[1]] + piecePositionScore
                elif piece[0] == 'b':
                    score -= PIECE_SCORE[piece[1]] + piecePositionScore

    return score