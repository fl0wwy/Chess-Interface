import pygame as pg
from abc import ABC, abstractmethod

class Player(ABC):
    def __init__(self, color, board) -> None:
        super().__init__()
        self.color = color
        self.board = board

    @abstractmethod
    def move(self):
        pass

class AI(Player):
    """Class that represents an AI
    """
    def __init__(self, color, board) -> None:
        super().__init__(color, board)

    def move(self):
        """Randomly generates a move
        """
        if self.board.to_move == self.color:
            en_passant = self.board.en_passant
            best_move = str(self.board.analyze_position(self.board.current_fen, self.board.ai_depth)[0])
            if "x" in best_move:
                best_move = best_move.replace("x", "")
            if len(best_move) == 5:
                best_move = best_move[:4]
            if best_move == "O-O":
                best_move = "e1g1" if self.color == "w" else "e8g8"
            elif best_move == "O-O-O":
                best_move = "e1c1" if self.color == "w" else "e8c8"

            try:
                piece = self.board.occ_squares[best_move[:2]]
                piece.play(self.board.square_dict[best_move[2::]])
            except KeyError:
                print(best_move)    

            self.board.to_move = "w" if self.board.to_move == "b" else "b"
            # updating move count, fen and en passant
            self.board.half_moves = str(int(self.board.half_moves) + 1)
            self.board.full_moves = str(int(self.board.full_moves) + 1) if self.color == "b" else self.board.full_moves
            if self.board.en_passant == en_passant:
                self.board.en_passant = "-"
            
            self.board.current_fen = self.board.gen_fen()
            
            if self.board.game_position_index == -1:
                self.board.game_positions.append(self.board.current_fen)
            else:
                self.board.game_positions = self.board.game_positions[:self.board.game_position_index]
                self.board.game_positions.append(self.board.current_fen)    
            
            self.board.position_analysis = self.board.analyze_position(self.board.current_fen, self.board.ai_depth)[1]

class Human(Player):
    """Class that represents a human player
    """
    def __init__(self, color, board) -> None:
        super().__init__(color, board)
        self.pressed = None

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
                        
                        if self.board.game_position_index == -1:
                            self.board.game_positions.append(self.board.current_fen)
                        else:
                            self.board.game_positions = self.board.game_positions[:self.board.game_position_index]
                            self.board.game_positions.append(self.board.current_fen)  
                        
                        self.board.position_analysis = self.board.analyze_position(self.board.current_fen, self.board.ai_depth)[1]
                        return
                if pg.mouse.get_pressed()[2]:
                    self.pressed.rect.center = self.board.square_dict[self.pressed.square].center
                    self.pressed.moves.clear()   
                    self.pressed = None   
            else:  
                for piece in self.board.pieces["white"].sprites() if self.color == "w" else self.board.pieces["black"].sprites(): 
                    if piece.rect.collidepoint(pg.mouse.get_pos()) and pg.mouse.get_pressed()[0]:
                        self.pressed = piece         
        
        