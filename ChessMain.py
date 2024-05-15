# This is our main driver file. It will be responsible for handling user input and displaying the current GameState Object.
import pygame as p
import ChessEngine

WIDTH = HEIGHT = 512 ## 400 is another good option for resolution
DIMENSIONS = 8 # board is 8x8 squares
SQ_SIZE = HEIGHT // DIMENSIONS
MAX_FPS = 15 #For animations later
IMAGES = {}

'''
Initialize a global dictionary of images. This will be called once in the main
'''

def loadImages():
    pieces = ['wp', 'bp', 'wK', 'wQ', 'wR', 'wB', 'wN', 'bK', 'bQ', 'bR', 'bB', 'bN']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("../Pictures/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

####
#The main driver for our code. THis will handle user input and updating the graphics
        
def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState() # Calls the constructor and creates an instance of GameState with the three variables
    validMoves = gs.getValidMoves()
    moveMade = False #Flag varibale for when a move is made

    loadImages() #only do this once before the while loop
    running = True
    sqSelected = () # no square is selected intially, keep track of the last click of the user, contains the row and column
    playerClicks = [] #keeps track of the player clicks (two tuples: (6, 4), (4, 4))

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos() # gets x and y location of the mouse
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE
                if sqSelected == (row, col): #checks to see if the user has selected the same square twice, if this happens we want to unselect it
                    sqSelected = () #deselect
                    playerClicks = [] #clears previous selections
                    print(f'selected: {playerClicks}')
                else: 
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)
                    print(f'selected: {playerClicks}')
                if len(playerClicks) == 2:
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    print(move.getChessNotation())
                    if move in validMoves:
                        moveMade = True
                        gs.makeMove(move)
                        sqSelected = () #resets user clicks
                        playerClicks = []
                    else:
                        playerClicks = [sqSelected]
                        
                    #key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True

        if moveMade:
            validMoves = gs.getValidMoves() # only gets valid moves when a move is actually made

        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()
            

"""
Responsible for all of the graphics with in the current game state
"""
def drawGameState(screen, gs):
    drawBoard(screen) # add these 2 in later
    drawPieces(screen, gs.board) #draws pieces ontop of those squares

"""
Draws the squares on the board. Top left square is always White for either perspective
"""
def drawBoard(screen):
    colors = [p.Color("white"), p.Color("dark gray")]
    for r in range(DIMENSIONS):
        for c in range(DIMENSIONS):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect((c*SQ_SIZE, r*SQ_SIZE), (SQ_SIZE, SQ_SIZE)))

"""
Draws the pieces on the board using the current GameState.board
"""
def drawPieces(screen, board):
    for r in range(DIMENSIONS):
        for c in range(DIMENSIONS):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect((c*SQ_SIZE, r*SQ_SIZE), (SQ_SIZE, SQ_SIZE)))

if __name__ == "__main__":
    main()

