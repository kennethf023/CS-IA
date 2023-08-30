# import pygame as p
# import ChessEngine
# import SmartMoveFinder
# WIDTH = HEIGHT = 512  # optional 400
# MOVE_LOG_WIDTH=250
# MOVE_LOG_HEIGHT=HEIGHT
# DIMENSION = 8  # dimensions are 8x8
# SQ_SIZE = HEIGHT // DIMENSION
# MAX_FPS = 15  # For animation
# IMAGES = {}

# def load_images():
#     pieces = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]
#     for piece in pieces:
#         IMAGES[piece] = p.transform.scale(p.image.load("Chess/images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
# #         note: we can access an image by saying 'IMAGES['wp']
# def main():
#     p.init()
#     screen = p.display.set_mode((WIDTH+MOVE_LOG_WIDTH, HEIGHT))
#     clock = p.time.Clock()
#     screen.fill(p.Color("white"))
#     moveLogFont=p.font.SysFont("Arial",12,False,False)
#     gs = ChessEngine.GameState()
#     validMoves=gs.getValidMoves()
#     moveMade=False
#     animate=False
#     load_images()  # only operated once
#     running = True
#     sqSelected=()
#     playerClicks=[]
#     gameOver=False
#     playerOne=True
#     playerTwo=False
#     while running:
#         humanTurn=(gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
#         for e in p.event.get():
#             if e.type == p.QUIT:
#                 running = False
#             elif e.type==p.MOUSEBUTTONDOWN:
#                 if not gameOver and humanTurn:
#                     location=p.mouse.get_pos()
#                     col=location[0]//SQ_SIZE
#                     row=location[1]//SQ_SIZE
#                     if sqSelected==(row,col) or col>=8:
#                         sqSelected=()
#                         playerClicks=[]
#                     else:
#                         sqSelected=(row,col)
#                         playerClicks.append(sqSelected)
#                     if len(playerClicks)==2:
#                         move=ChessEngine.Move(playerClicks[0],playerClicks[1],gs.board)
#                         for i in range(len(validMoves)):
#                             if move == validMoves[i]:
#                                 gs.makeMove(validMoves[i])
#                                 moveMade=True
#                                 animate=True
#                                 sqSelected=()
#                                 playerClicks=[]
#                         if not moveMade:
#                             playerClicks=[sqSelected]
#             elif e.type==p.KEYDOWN:
#                 if e.key==p.K_z:
#                     gs.undoMove()
#                     moveMade=True
#                     animate=False
#                     gameOver=False
#                 if e.key==p.K_r:
#                     gs=ChessEngine.GameState()
#                     validMoves=gs.getValidMoves()
#                     sqSelected=()
#                     playerClicks=[]
#                     moveMade=False
#                     animate=False
#                     gameOver=False
#         if not gameOver and not humanTurn:
#             AIMove=SmartMoveFinder.findBestMove(gs,validMoves)
#             if AIMove is None:
#                 AIMove=SmartMoveFinder.findRandomMove(validMoves)
#             gs.makeMove(AIMove)
#             moveMade=True
#             animate=True
#         if moveMade:
#             if animate:
#                 animateMove(gs.moveLog[-1],screen,gs.board,clock)
#             validMoves=gs.getValidMoves()
#             moveMade=False
#             animate=False
#         drawGameState(screen, gs,validMoves,sqSelected,moveLogFont)
#         if gs.checkmate:
#             gameOver=True
#             if gs.whiteToMove:
#                 text="Black wins by checkmate"
#             else:
#                 text="White wins by checkmate"
#         elif gs.stalemate:
#             gameOver=True 
#             text="Stalemate"
#         drawEndGameText(screen,text)

#         clock.tick(MAX_FPS)
#         p.display.flip()

# def highlightSquares(screen,gs,validMoves,sqSelected):
#     if sqSelected!=():
#         r,c=sqSelected
#         if gs.board[r][c][0]==('w' if gs.whiteToMove else 'b'):
#             s=p.Surface((SQ_SIZE,SQ_SIZE))
#             s.set_alpha(100)
#             s.fill(p.Color("blue"))
#             screen.blit(s,(c*SQ_SIZE,r*SQ_SIZE))
#             s.fill(p.Color("yellow"))
#             for move in validMoves:
#                 if move.startRow==r and move.startCol==c:
#                     screen.blit(s,(SQ_SIZE*move.endCol,SQ_SIZE*move.endRow))

# def drawGameState(screen, gs,validMoves,sqSelected,moveLogFont):
#     drawBoard(screen) #draw squares on board
#     highlightSquares(screen,gs,validMoves,sqSelected)
#     drawPieces(screen, gs.board)
#     drawMoveLog(screen,gs,moveLogFont)

# def drawBoard(screen):
#     global colors
#     colors = [p.Color("white"), p.Color("grey")]
#     for r in range(DIMENSION):
#         for c in range(DIMENSION):
#             color = colors[((r+c) % 2)]
#             p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


# def drawPieces(screen, board):
#     for r in range(DIMENSION):
#         for c in range(DIMENSION):
#             piece=board[r][c]
#             if piece!="--":
#                 screen.blit(IMAGES[piece],p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))

# def drawMoveLog(screen,gs,font):
#     moveLogRect=p.Rect(WIDTH,0,MOVE_LOG_WIDTH,MOVE_LOG_HEIGHT)
#     p.draw.rect(screen,p.Color("black"),moveLogRect)
#     moveLog=gs.moveLog
#     moveTexts=moveLog
#     padding=5
#     for i in range(len(moveTexts)):
#         text=moveTexts[i].getChessNotation()
#         textObject=font.render(text,True,p.Color("White"))
#         textLocation=moveLogRect.move(padding,padding)
#         screen.blit(textObject,textLocation)

# def animateMove(move,screen,board,clock):
#     global colors
#     coords=[]
#     dR=move.endRow-move.startRow
#     dC=move.endCol-move.startCol
#     framesPerSquare=10
#     frameCount=(abs(dR)+abs(dC))*framesPerSquare
#     for frame in range(frameCount+1):
#         r,c=(move.startRow+dR*frame/frameCount,move.startCol+dC*frame/frameCount)
#         drawBoard(screen)
#         drawPieces(screen,board)
#         color=colors[(move.endRow+move.endCol)%2]
#         endSquare=p.Rect(move.endCol*SQ_SIZE,move.endRow*SQ_SIZE,SQ_SIZE,SQ_SIZE)
#         p.draw.rect(screen,color,endSquare)
#         if move.pieceCaptured!="--":
#             if move.isEnpassantMove:
#                 enPassantRow=move.endRow+1 if move.pieceCaptured[0]=='b' else move.endRow-1
#                 endSquare=p.Rect(move.endCol*SQ_SIZE,move.enPassantRow*SQ_SIZE,SQ_SIZE,SQ_SIZE)
#             screen.blit(IMAGES[move.pieceCaptured],endSquare)
#         screen.blit(IMAGES[move.pieceMoved],p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))
#         p.display.flip()
#         clock.tick(60)

# def drawEndGameText(screen,text):
#     font=p.font.SysFont("Helvetica",32,True,False)
#     textObject=font.render(text,0,p.Color("Gray"))
#     textLocation=p.Rect(0,0,WIDTH,HEIGHT).move(WIDTH/2-textObject.get_width()/2,HEIGHT/2-textObject.get_height()/2)
#     screen.blit(textObject,textLocation)
#     textObject=font.render(text,0,p.Color("Black"))
#     screen.blit(textObject,textLocation.move(2,2))



# if __name__ == "__main__":
#     main()
