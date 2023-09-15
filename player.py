import pygame as pg
from random import choice
from time import sleep

class AI:
    """Class that represents an AI
    """
    def __init__(self, color, board) -> None:
        self.color = color
        self.board = board

    def move(self):
        """Randomly generates a move
        """
        if self.board.to_move == self.color:
            en_passant = self.board.en_passant
            sleep(0.1)
            depth = 0
            piece = choice(self.board.pieces["black"].sprites()) if self.color == "b" else choice(self.board.pieces["white"].sprites())
            while piece.possible_moves() == []:
                depth += 1
                piece = choice(self.board.pieces["black"].sprites()) if self.color == "b" else choice(self.board.pieces["white"].sprites())
                if depth >= len(self.board.pieces["black"].sprites()) if self.color == "b" else len(self.board.pieces["white"].sprites()):
                    return
            piece.play(choice(piece.possible_moves()))
            self.board.to_move = "w" if self.board.to_move == "b" else "b"
            # updating move count, fen and en passant
            self.board.half_moves = str(int(self.board.half_moves) + 1)
            self.board.full_moves = str(int(self.board.full_moves) + 1) if self.color == "b" else self.board.full_moves
            if self.board.en_passant == en_passant:
                self.board.en_passant = "-"
            self.board.current_fen = self.board.gen_fen()

class Human:
    """Class that represents a human player
    """
    def __init__(self, color, board) -> None:
        self.color = color
        self.board = board
        self.pressed = None # piece that is pressed by the player

    def move(self, display):   
        """Generates, possible moves for a selected piece, displays possible moves on screen and executes a move once chosen.

        Args:
            display (pg.display): the display obj which the moves are to be displayed on
        """
        if self.board.to_move == self.color:
            en_passant = self.board.en_passant
            for piece in self.board.pieces["white"].sprites() if self.color == "w" else self.board.pieces["black"].sprites():
                if piece == self:
                    continue
                if piece.pressed:
                    return
            
            if self.pressed is not None:
                if self.pressed.moves == []:
                    self.pressed.moves = self.pressed.possible_moves() or []

                self.pressed.rect.center = pg.mouse.get_pos()
                for rect in self.pressed.moves:
                    pg.draw.ellipse(display, "#3E2723", rect.scale_by(0.4, 0.4))
                    if rect.collidepoint(pg.mouse.get_pos()) and pg.mouse.get_pressed()[0]:
                        self.pressed.play(rect)
                        # Switch playing side, clear current move list and move the piece to its new square
                        self.pressed.moves.clear()
                        self.pressed = None
                        self.board.to_move = "b" if self.board.to_move == "w" else "w"
                        # updating move count, fen and en passant
                        self.board.half_moves = str(int(self.board.half_moves) + 1)
                        self.board.full_moves = str(int(self.board.full_moves) + 1) if self.color == "b" else self.board.full_moves
                        if self.board.en_passant == en_passant:
                            self.board.en_passant = "-"
                        self.board.current_fen = self.board.gen_fen()
                        return
                if pg.mouse.get_pressed()[2]:
                    self.pressed.rect.center = self.board.square_dict[self.pressed.square].center
                    self.pressed.moves.clear()   
                    self.pressed = None   
            else:  
                for piece in self.board.pieces["white"].sprites() if self.color == "w" else self.board.pieces["black"].sprites(): 
                    if piece.rect.collidepoint(pg.mouse.get_pos()) and pg.mouse.get_pressed()[0]:
                        self.pressed = piece         
        
        