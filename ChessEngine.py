# This class is responsible for storing all the information about the current state of a chess game. IT will also be responsible for 
# determining the valid moves at the current state. It will also keep a move log. 

class GameState():
    # Constructor:
    def __init__(self):
        #Board is 8x8 2D list. each element of the list has 2 characters; the first is the color of the piece and the second is the type of the piece
        #'--' resresents an empty space
        
        ######## ACTUAL BOARD (DO NOT MODIFY) 
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
        ]

        ######### TEST BOARD
        # self.board = [
        #     ['--', '--', '--', '--', '--', '--', '--', '--'],
        #     ['bp', '--', '--', '--', '--', '--', '--', '--'],
        #     ['--', '--', 'bK', '--', 'bQ', 'bB', '--', '--'],
        #     ['--', '--', '--', '--', '--', 'wK', '--', '--'],
        #     ['--', '--', '--', '--', '--', '--', '--', '--'],
        #     ['--', '--', '--', 'wN', '--', 'wQ', '--', '--'],
        #     ['--', '--', '--', '--', '--', '--', 'bp', '--'],
        #     ['wR', '--', '--', '--', '--', '--', '--', 'wR'],
        # ]
        

        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves, 
                              'B': self.getBishopMoves, 'K': self.getKingMoves, 'Q': self.getQueenMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)

    '''
    Takes a move as a parameter and executes it. This will not work for castling, Enpassant, pawn promotion.
    '''
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove #changes player to move
        #update the kings location if moved
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)
            
        


    '''
    This will undo the previous move
    '''
    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            #update the kings position
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)


    '''
    All moves considering checks
    '''
    def getValidMoves(self):
        #1. generat eall the possible moves
        moves = self.getAllPossibleMoves()
        #2. for each move make the move
        for i in range(len(moves)-1, -1, -1): #when removing from a list, iterate backwards through the list
            self.makeMove(moves[i])
            #3. generate all the opponents moves
            #4. for of your opponents moves see if they attack your king
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])  #5. if they do attack your king, not a valid move
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        return moves
    
    '''
    Get all possible pins and checks
    '''
    def checkForPinsAndChecks(self):
        pins = [] #squares where friendly pinned pieces are and direction of the pin
        checks = [] #squares where enemy is applying the check
        inCheck = False
        if self.whiteToMove:
            enemyColor = 'b'
            allyColor = 'w'
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = 'w'
            allyColor = 'b'
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
            
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            piecesBlocking = 0
            aroundKing = []
            d = directions[j]
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    piece = self.board[endRow][endCol]
                    if piece[0] == enemyColor:
                        if (piece[1] == 'B' and 0 <= j <= 3) or \
                            (piece[1] == 'R' and 4 <= j <= 7) or \
                                (piece[1] == 'Q') or (piece[1] == 'K' and i == 1) or \
                                    (piece[1] == 'p' and (j == 7 or j == 5) and i == 1):
                                        if piecesBlocking == 0: ## check, now piece in between king and attacking piece
                                            checks.append((endRow, endCol, d[0], d[1]))
                                        elif piecesBlocking == 1: ## Pin if 1 piece is blocking attacking piece
                                            pins.append(possiblePin)
                        else:
                            piecesBlocking += 1
                    elif piece[0] == allyColor:
                        piecesBlocking += 1
                        possiblePin = (endRow, endCol, d[0], d[1])
                else: ## off board
                    break
            return checks, pins
            


    '''
    will determine if the current player is in check
    '''
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])
    
    
    '''
    determine if the enemy can attack the square r, c
    '''
    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False
            

    """
    All moves without considering checks
    """
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)): # number of rows
            for c in range(len(self.board[r])): #number of columns in a row
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves) #calls the appropriate move function based on the piece type
        return moves

    '''
    This will get all the pawn moves located at row, column and add these moves to the list
    '''
    def getPawnMoves(self, r, c, moves): # Still need to fix index out of bounds, en passant and pawn p
        if self.whiteToMove: #white pawn moves
            if self.board[r] == 0:
                self.board[r][c][1] == "Q"
            else:
                if self.board[r-1][c] == '--': #1 square pawn advance
                    moves.append(Move((r,c), (r-1, c), self.board))
                    if r == 6 and self.board[r-2][c] == '--':
                        moves.append(Move((r,c), (r-2, c), self.board))
                if c-1 >= 0: # makes sure we don't capturing off the board on column '-1', Captures to the left
                    if self.board[r-1][c-1][0] == 'b': #make sure it is an enemy piece to be captured
                        moves.append(Move((r, c), (r-1, c-1), self.board))
                if c+1 <= 7: #captures to the right
                    if self.board[r-1][c+1][0] == 'b':
                        moves.append(Move((r, c), (r-1, c+1), self.board))
    
        else: #Black pawn moves
            if self.board[r] == 7:
                print("test")
                self.board[r][c][1] == "Q"
            else:
                if self.board[r+1][c] == '--':
                    moves.append(Move((r,c), (r+1, c), self.board))
                    if r == 1 and self.board[r+2][c] == '--':
                        moves.append(Move((r,c), (r+2, c), self.board))
                if c-1 >= 0: 
                    if self.board[r+1][c-1][0] == 'w': #make sure it is an enemy piece to be captured
                        moves.append(Move((r, c), (r+1, c-1), self.board))
                if c+1 <= 7: #captures to the right
                    if self.board[r+1][c+1][0] == 'w':
                        moves.append(Move((r, c), (r+1, c+1), self.board))


    def getBishopMoves(self, r, c, moves):
        if self.whiteToMove:
            for i in range(1, 8):
                if r-i >= 0 and c-i >= 0:
                    if self.board[r-i][c-i] == '--':
                        moves.append(Move((r,c), (r-i, c-i), self.board))
                    if self.board[r-i][c-i][0] == 'b':
                        moves.append(Move((r,c), (r-i, c-i), self.board))
                        break
                if r-i >= 0 and c+i <= 7:
                    if self.board[r-i][c+i] == '--':
                        moves.append(Move((r,c), (r-i, c+i), self.board))
                    if self.board[r-i][c+i][0] == 'b':
                        moves.append(Move((r,c), (r-i, c+i), self.board))
                        break
                if r+i <= 7 and c-i >= 0:
                    if self.board[r+i][c-i] == '--':
                        moves.append(Move((r,c), (r+i, c-i), self.board))
                    if self.board[r+i][c-i][0] == 'b':
                        moves.append(Move((r,c), (r+i, c-i), self.board))
                        break
                if r+i <= 7 and c+i <= 7:
                    if self.board[r+i][c+i] == '--':
                        moves.append(Move((r,c), (r+i, c+i), self.board))
                    if self.board[r+i][c+i][0] == 'b':
                        moves.append(Move((r,c), (r+i, c+i), self.board))
                        break
        else:
            for i in range(1, 8):
                if r-i >= 0 and c-i >= 0:
                    if self.board[r-i][c-i] == '--':
                        moves.append(Move((r,c), (r-i, c-i), self.board))
                    if self.board[r-i][c-i][0] == 'w':
                        moves.append(Move((r,c), (r-i, c-i), self.board))
                        break
                if r-i >= 0 and c+i <= 7:
                    if self.board[r-i][c+i] == '--':
                        moves.append(Move((r,c), (r-i, c+i), self.board))
                    if self.board[r-i][c+i][0] == 'w':
                        moves.append(Move((r,c), (r-i, c+i), self.board))
                        break
                if r+i <= 7 and c-i >= 0:
                    if self.board[r+i][c-i] == '--':
                        moves.append(Move((r,c), (r+i, c-i), self.board))
                    if self.board[r+i][c-i][0] == 'w':
                        moves.append(Move((r,c), (r+i, c-i), self.board))
                        break
                if r+i <= 7 and c+i <= 7:
                    if self.board[r+i][c+i] == '--':
                        moves.append(Move((r,c), (r+i, c+i), self.board))
                    if self.board[r+i][c+i][0] == 'w':
                        moves.append(Move((r,c), (r+i, c+i), self.board))
                        break

    '''
    This will get all the rook moves located at row, column and add these moves to the list
    '''
    def getRookMoves(self, r, c, moves): # need to add castling
        if self.whiteToMove:
            for i in range(1, 8):
                if r-i >= 0:
                    if self.board[r-i][c] == '--':
                        moves.append(Move((r,c), (r-i,c), self.board))
                    if self.board[r-i][c][0] == 'b':
                        moves.append(Move((r,c), (r-i,c), self.board))
                        break
                if r+i <= 7:
                    if self.board[r+i][c] == '--':
                        moves.append(Move((r,c), (r+i,c), self.board))
                    if self.board[r+i][c][0] == 'b':
                        moves.append(Move((r,c), (r+i,c), self.board))
                        break
                if c-i >= 0:
                    if self.board[r][c-i] == '--':
                        moves.append(Move((r,c), (r,c-i), self.board))
                    if self.board[r][c-i][0] == 'b':
                        moves.append(Move((r,c), (r,c-i), self.board))
                        break
                if c+i <= 7:
                    if self.board[r][c+i] == '--':
                        moves.append(Move((r,c), (r,c+i), self.board))
                    if self.board[r][c+i][0] == 'b':
                        moves.append(Move((r,c), (r,c+i), self.board))
                        break
        else:
            for i in range(1, 8):
                if r-i >= 0:
                    if self.board[r-i][c] == '--':
                        moves.append(Move((r,c), (r-i,c), self.board))
                    if self.board[r-i][c][0] == 'w':
                        moves.append(Move((r,c), (r-i,c), self.board))
                        break
                if r+i <= 7:
                    if self.board[r+i][c] == '--':
                        moves.append(Move((r,c), (r+i,c), self.board))
                    if self.board[r+i][c][0] == 'w':
                        moves.append(Move((r,c), (r+i,c), self.board))
                        break
                if c-i >= 0:
                    if self.board[r][c-i] == '--':
                        moves.append(Move((r,c), (r,c-i), self.board))
                    if self.board[r][c-i][0] == 'w':
                        moves.append(Move((r,c), (r,c-i), self.board))
                        break
                if c+i <= 7:
                    if self.board[r][c+i] == '--':
                        moves.append(Move((r,c), (r,c+i), self.board))
                    if self.board[r][c+i][0] == 'w':
                        moves.append(Move((r,c), (r,c+i), self.board))
                        break
            
    
    def getKnightMoves(self, r, c, moves):
        knightMoves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                    (1, -2), (1, 2), (2, -1), (2, 1)]
        
        if self.whiteToMove:
            for move in knightMoves:
                newRow = r + move[0]
                newCol = c + move[1]
                
                if 0 <= newRow <= 7 and 0 <= newCol <= 7:
                    if self.board[newRow][newCol] == '--' or self.board[newRow][newCol][0] == 'b':
                        moves.append(Move((r, c), (newRow, newCol), self.board))
        else:
            for move in knightMoves:
                newRow = r + move[0]
                newCol = c + move[1]
                
                if 0 <= newRow <= 7 and 0 <= newCol <= 7:
                    if self.board[newRow][newCol] == '--' or self.board[newRow][newCol][0] == 'w':
                        moves.append(Move((r, c), (newRow, newCol), self.board))



    def getQueenMoves(self, r, c, moves):
        queenMoves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        if self.whiteToMove:
            for direction in queenMoves:
                dr, dc = direction
                
                for i in range(1, 8):
                    new_r = r + i * dr
                    new_c = c + i * dc
                    
                    if 0 <= new_r < 8 and 0 <= new_c < 8:
                        target_piece = self.board[new_r][new_c]
                        
                        if target_piece == '--':
                            moves.append(Move((r, c), (new_r, new_c), self.board))
                        elif target_piece[0] == 'b':
                            moves.append(Move((r, c), (new_r, new_c), self.board))
                            break
                    else:
                        break
        else:
            for direction in queenMoves:
                dr, dc = direction
                
                for i in range(1, 8):
                    new_r = r + i * dr
                    new_c = c + i * dc
                    
                    if 0 <= new_r < 8 and 0 <= new_c < 8:
                        target_piece = self.board[new_r][new_c]
                        
                        if target_piece == '--':
                            moves.append(Move((r, c), (new_r, new_c), self.board))
                        elif target_piece[0] == 'w':
                            moves.append(Move((r, c), (new_r, new_c), self.board))
                            break
                    else:
                        break
                    
            
                        
                        
    def getKingMoves(self, r, c, moves):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (-1, 1), (1, -1)]
        board_height = len(self.board)
        board_width = len(self.board[0])
        color = 'b' if self.whiteToMove else 'w'

        for direction in directions:
            dr, dc = direction
            new_r, new_c = r + dr, c + dc
            
            if 0 <= new_r < board_height and 0 <= new_c < board_width:
                target_piece = self.board[new_r][new_c]
                
                if target_piece == '--' or target_piece[0] == color:
                    moves.append(Move((r, c), (new_r, new_c), self.board))

            
            


class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v:k for k, v in ranksToRows.items()}
    filesToCol = {"a": 0, "b": 1, "c": 2, "d": 3,
                  "e": 4, "f": 5, "g": 6, "h": 7}
    colToFiles = {v: k for k, v in filesToCol.items()}
    # Constructor
    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    """
    Overriding the equals
    """
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colToFiles[c] + self.rowsToRanks[r]

        