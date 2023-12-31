
import pygame as p
import ChessEngine
import SmartMoveFinder
from multiprocessing import Process, Queue

BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8  # Dimensions of a chess board are 8x8
FEEDBACK_HEIGHT=50
SQ_SIZE = BOARD_HEIGHT // DIMENSION
FEEDBACK_SIZE = 20
MAX_FPS = 15  # Mainly for animations
IMAGES = {}
FEEDBACK_IMAGES={}
COLORS = [p.Color("white"), p.Color("gray")]

"""
Initialize global dictionary of images. 
This will be called exactly once in the main function
"""
def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']

    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("Chess/images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


"""
The main driver for the code. 
It will handle user input and updating the graphics
"""
def main():
    FEEDBACK_IMAGES['mistake'] = p.transform.scale(p.image.load("Chess/images/mistake.png"), (FEEDBACK_SIZE, FEEDBACK_SIZE))
    FEEDBACK_IMAGES['blunder'] = p.transform.scale(p.image.load("Chess/images/blunder.png"), (FEEDBACK_SIZE, FEEDBACK_SIZE))
    FEEDBACK_IMAGES['good'] = p.transform.scale(p.image.load("Chess/images/good.png"), (FEEDBACK_SIZE, FEEDBACK_SIZE))
    FEEDBACK_IMAGES['best'] = p.transform.scale(p.image.load("Chess/images/best.png"), (FEEDBACK_SIZE, FEEDBACK_SIZE))

    p.init()
    p.mixer.init()
    screen = p.display.set_mode([BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT+FEEDBACK_HEIGHT])
    clock = p.time.Clock()
    moveLogFont = p.font.SysFont("Arial", 14, False, False)
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    sqSelected = ()  # keep track of last user click, tuple: (row, col)
    newSqSelected=()
    playerClicks = []  # keep track of last two player clicks, two tuples: [(row, col), (row, col)]
    playerOne = True  # If true, human is playing white, otherwise AI is playing white
    playerTwo = False  # same as above, except playing black
    moveFinderProcess = None
    returnQueue = None
    AIThinking = False
    gameOver = False
    moveMade = False
    moveUndone = False
    animate = False
    running = True
    analysis=True

    loadImages()
    difficultyLeft = 1
    difficultyRight = 10
    currentDifficulty = 5
    score = 0
    lastScore=0
    bestMove = None
    while running:
        isHumanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        # score = SmartMoveFinder.getScore(gs,validMoves) * -1 if not isHumanTurn else 1
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE

                    if sqSelected == (row, col) or col >= 8:  # user clicked the same square twice or the move log
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2 and isHumanTurn:
                        newSqSelected=playerClicks[1]
                        # bestMove=SmartMoveFinder.getBestMove(gs,validMoves)
                        bestMove=SmartMoveFinder.findRandomMove(validMoves)
                        if sqSelected == (5,0):
                            bestMove=ChessEngine.Move((6,3),(4,3),gs.board,False, False)
                        if sqSelected == (5,5):
                            bestMove=ChessEngine.Move((7,6),(5,5),gs.board,False, False)
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_u:
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True
                if e.key == p.K_r:
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True
                if e.key == p.K_a:
                    analysis=not analysis
        if not gameOver and not isHumanTurn and not moveUndone:
            if not AIThinking:
                AIThinking = True
                returnQueue = Queue()  # used to pass data between threads
                moveFinderProcess = Process(target=SmartMoveFinder.findBestMove,
                 args=(gs, validMoves, returnQueue, currentDifficulty//3))
                moveFinderProcess.start()
                score = -SmartMoveFinder.getScore(gs,validMoves)
                # bestMove=SmartMoveFinder.getBestMove(gs,validMoves)
                # print(bestMove)

            if not moveFinderProcess.is_alive():
                AIMove = returnQueue.get()
                if AIMove is None:
                    AIMove = SmartMoveFinder.findRandomMove(validMoves)
                gs.makeMove(AIMove)
                moveMade = True
                animate = True
                AIThinking = False
        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            # moveMade = False
            animate = False
            moveUndone = False
            # score = SmartMoveFinder.getScore(gs,validMoves) * 1 if gs.whiteToMove else -1

        if gs.checkmate or gs.stalemate:
            gameOver = True
            if gs.stalemate:
                text = "Stalemate"
            else:
                if gs.whiteToMove:
                    text = "Black wins by checkmate" 
                    difficultyRight=currentDifficulty
                    currentDifficulty=(difficultyLeft+difficultyRight)//2
                    score = -1000

                else:
                    text = "White wins by checkmate"
                    difficultyLeft=currentDifficulty
                    currentDifficulty=(difficultyLeft+difficultyRight)//2
                    score = 1000
            gs.stalemate=gs.checkmate=False
        drawGameState(screen, gs, validMoves, sqSelected, moveLogFont, currentDifficulty,score,lastScore,newSqSelected,not gs.whiteToMove, analysis, bestMove)
        if moveMade:
            moveMade = False
            lastScore=score

        if gameOver:
            drawEndGameText(screen, text)

        clock.tick(MAX_FPS)
        p.display.flip()


"""
Responsible for all the graphics within a current game state
"""
def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont, currentDifficulty,score,lastScore,newSqSelected,whiteToMove,analysis, bestMove):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    if whiteToMove and analysis: 
        feedback(screen,score-lastScore,newSqSelected, bestMove, moveLogFont)
    drawPieces(screen, gs.board)
    drawMoveLog(screen, gs, moveLogFont)
    printEvaluation(screen,score,moveLogFont)
    printScore(screen, currentDifficulty, moveLogFont)



"""
Draws the squares on the board.
In chess, the top left square is always light.
"""
def drawBoard(screen):
    global COLORS
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = COLORS[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


"""
Highlight square selection
"""
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            # highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

            # highlight valid moves from that square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))

def feedback(screen, dif, sqSelected, bestMove,font):
    if(sqSelected!=()):
        moveLogRect = p.Rect(0, BOARD_HEIGHT, BOARD_WIDTH, FEEDBACK_HEIGHT)
        p.draw.rect(screen, p.Color("black"), moveLogRect)
        padding = 5
        text=""
        r, c = sqSelected
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)
        if dif<=-3:
            s.fill(p.Color('red'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            screen.blit(FEEDBACK_IMAGES['blunder'], p.Rect(c * SQ_SIZE - 10, r * SQ_SIZE - 10, FEEDBACK_SIZE, FEEDBACK_SIZE))
            text="Blunder! You should have played " + str(bestMove) + " instead."
        elif dif<=-1.5:
            s.fill(p.Color('orange'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            screen.blit(FEEDBACK_IMAGES['mistake'], p.Rect(c * SQ_SIZE- 10, r * SQ_SIZE - 10, FEEDBACK_SIZE, FEEDBACK_SIZE))
            text="Inaccuracy. You should have played " + str(bestMove) + " instead."
        elif dif<-0.1:
            s.fill(p.Color(178,172,136))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            screen.blit(FEEDBACK_IMAGES['good'], p.Rect(c * SQ_SIZE- 10, r * SQ_SIZE - 10, FEEDBACK_SIZE, FEEDBACK_SIZE))
            text="Good move. " + str(bestMove) + " would've been even better."
        else:
            s.fill(p.Color('green'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            screen.blit(FEEDBACK_IMAGES['best'], p.Rect(c * SQ_SIZE- 10, r * SQ_SIZE - 10, FEEDBACK_SIZE, FEEDBACK_SIZE))
            text="Excellent! You played the best move!"
        # print(bestMove)
        textObject = font.render(text, True, p.Color('White'))
        textLocation = moveLogRect.move(padding, padding)
        screen.blit(textObject, textLocation)
    # print(dif)



"""
Draws the pieces on top of the board using the current GameState.board
"""
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]

            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


"""
Draws the move log on the right side of the window
"""
def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i // 2 + 1) + ". " + str(moveLog[i]) + " "
        if i + 1 < len(moveLog):  # append opponent move
            moveString += str(moveLog[i + 1]) + "  "
        moveTexts.append(moveString)

    movesPerRow = 2
    padding = 5
    lineSpacing = 2
    textY = padding

    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i + j]

        textObject = font.render(text, True, p.Color('White'))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing

def printScore(screen, score, font):
    moveLogRect = p.Rect(BOARD_WIDTH, 480, MOVE_LOG_PANEL_WIDTH, 30)
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    

    padding = 5
    text="AI Difficulty Level (1-10): "+str(score)
    textObject = font.render(text, True, p.Color('White'))
    textLocation = moveLogRect.move(padding, padding)
    screen.blit(textObject, textLocation)

def printEvaluation(screen, score, font):
    moveLogRect = p.Rect(BOARD_WIDTH, 400, MOVE_LOG_PANEL_WIDTH, 30)
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    

    padding = 5
    if score ==1000:
        text="Score: 1 - 0"
    elif score == -1000:
        text="Score: 0 - 1"
    else:
        text="Score: "+str(score)
    textObject = font.render(text, True, p.Color('White'))
    textLocation = moveLogRect.move(padding, padding)
    screen.blit(textObject, textLocation)

"""
Animating a move including playing the sound
"""
def animateMove(move, screen, board, clock):
    if move.isCapture:
        p.mixer.music.load("Chess/audio/capture.mp3")
        p.mixer.music.play()
    else:
        p.mixer.music.load("Chess/audio/move.mp3")
        p.mixer.music.play()

    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 7
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare

    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount)
        drawBoard(screen)
        drawPieces(screen, board)

        # erase the piece moved from its ending square
        color = COLORS[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)

        # draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            if move.isEnpassantMove:
                enPassantRow = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                endSquare = p.Rect(move.endCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        if move.pieceMoved != '--':
            screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

        p.display.flip()
        clock.tick(60)


"""
Draw text on screen
"""
def drawEndGameText(screen, text):
    # Draw text shadow
    font = p.font.SysFont("Helvetica", 32, True, False)
    textObject = font.render(text, False, p.Color('Gray'))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObject.get_width() / 2,
                                                                BOARD_HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)

    # Draw main text
    textObject = font.render(text, False, p.Color("Black"))
    screen.blit(textObject, textLocation.move(2, 2))


if __name__ == "__main__":
    main()