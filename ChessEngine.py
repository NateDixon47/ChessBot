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
        self.inCheck = False
        self.pins = []
        self.checks = []

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
        moves = self.getAllPossibleMoves()
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        
        if self.whiteToMove:
            kingRow, kingCol = self.whiteKingLocation
        else:
            kingRow, kingCol = self.blackKingLocation

        if self.inCheck:
            if len(self.checks) == 1:
                check = self.checks[0]
                checkRow, checkCol, dRow, dCol = check
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []

                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + dRow * i, kingCol + dCol * i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break

                for i in range(len(moves) - 1, -1, -1):
                    move = moves[i]
                    if move.pieceMoved[1] != 'K':
                        if (move.endRow, move.endCol) not in validSquares:
                            moves.remove(moves[i])
                    elif (move.startRow, move.startCol) in [(p[0], p[1]) for p in self.pins]:
                        moves.remove(moves[i])
            else:
                moves = []
                self.getKingMoves(kingRow, kingCol, moves)
        else:
            if len(self.pins) != 0:
                for pin in self.pins:
                    pinnedPiecePosition = (pin[0], pin[1])
                    pinDirection = (pin[2], pin[3])
                    for i in range(len(moves) - 1, -1, -1):
                        move = moves[i]
                        if (move.startRow, move.startCol) == pinnedPiecePosition:
                            if not self.isMoveAlongPinDirection(pinnedPiecePosition, (move.endRow, move.endCol), pinDirection):
                                moves.remove(moves[i])

        return moves

    def isMoveAlongPinDirection(self, startPos, endPos, direction):
        startRow, startCol = startPos
        endRow, endCol = endPos
        dRow, dCol = direction

        moveDirRow = endRow - startRow
        moveDirCol = endCol - startCol

        if dRow == 0:  # Horizontal pin
            return moveDirRow == 0
        elif dCol == 0:  # Vertical pin
            return moveDirCol == 0
        elif abs(dRow) == abs(dCol):  # Diagonal pin
            return abs(moveDirRow) == abs(moveDirCol) and moveDirRow * dRow > 0 and moveDirCol * dCol > 0
        else:
            return False
    
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
            d = directions[j]
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                #print(f'piecesBlocking: {piecesBlocking}')
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    piece = self.board[endRow][endCol]
                    if piece[0] == enemyColor:
                        if (piece[1] == 'B' and 0 <= j <= 3) or \
                            (piece[1] == 'R' and 4 <= j <= 7) or \
                                (piece[1] == 'Q') or (piece[1] == 'K' and i == 1) or \
                                    (piece[1] == 'p' and (j == 7 or j == 5) and i == 1):
                                        #print('in big conditional')
                                        if piecesBlocking == 0: ## check, now piece in between king and attacking piece
                                            inCheck = True
                                            if inCheck: print(f'incheck: {inCheck}')
                                            checks.append((endRow, endCol, d[0], d[1]))
                                        elif piecesBlocking == 1: ## Pin if 1 piece is blocking attacking piece
                                            print(f'pin: {self.board[possiblePin[0]][possiblePin[1]]}')
                                            pins.append(possiblePin)
                        else:
                            piecesBlocking += 1
                    elif piece[0] == allyColor:
                        piecesBlocking += 1
                        possiblePin = (endRow, endCol, d[0], d[1])
                else: ## off board
                    break
        return inCheck, pins, checks
    
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
        piecePinned = False
        pinDirection = []
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        if self.whiteToMove: #white pawn moves
            if self.board[r-1][c] == '--':
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((r,c), (r-1, c), self.board))
                    if r == 6 and self.board[r-2][c] == '--': # moves 2 squares for first move
                        moves.append(Move((r,c), (r-2,c), self.board))

            if c-1 >= 0: # captures to the left
                if self.board[r-1][c-1][0] == 'b':
                    if not piecePinned or pinDirection == (-1, -1):
                        moves.append(Move((r, c), (r-1, c-1), self.board))
                        
            if c+1 <= 7: # captures to the left
                if self.board[r-1][c+1][0] == 'b':
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(Move((r, c), (r-1, c+1), self.board))
    
        else: #Black pawn moves
            if self.board[r+1][c] == '--':
                if not piecePinned or pinDirection == (1,0):
                    moves.append(Move((r,c), (r+1, c-1), self.board))
                if r == 1 and self.board[r+2][c] == '--':
                    moves.append(Move((r, c), (r+2, c), self.board))
                    
            if c-1 >= 0:
                if self.board[r+1][c-1][0] == 'w':
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(Move((r, c), (r+1, c-1), self.board))
            if c+1 <= 7:
                if self.board[r+1][c+1][0] == 'w':
                    if not piecePinned or pinDirection == (1, 1):
                        moves.append(Move((r, c), (r+1, c+1), self.board))


    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                break
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--':
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else: # friendly piece
                            break
                else: # off the board
                    break
    '''
    This will get all the rook moves located at row, column and add these moves to the list
    '''
    def getRookMoves(self, r, c, moves): # need to add castling
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--':
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else: # friendly piece
                            break
                else: # off the board
                    break
            
    
    def getKnightMoves(self, r, c, moves):
        knightMoves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                    (1, -2), (1, 2), (2, -1), (2, 1)]
        
        piecePinned = False
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        allyColor = 'w' if self.whiteToMove else 'b'
        
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:
                        moves.append(Move((r,c), (endRow, endCol), self.board))



    def getQueenMoves(self, r, c, moves):
        self.getBishopMoves(r, c, moves)
        self.getRookMoves(r, c, moves)
                    
                                
    def getKingMoves(self, r, c, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = 'w' if self.whiteToMove else 'b'
        
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r,c), (endRow, endCol), self.board))
                    
                    if allyColor == 'w':
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)
            


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

        