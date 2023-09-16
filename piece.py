from abc import ABC, abstractmethod
import calc
from typing import Any
import pygame as pg

class Piece(ABC, pg.sprite.Sprite):
    def __init__(self, square : str , board : Any, color : str, icon : str, points : int) -> None:
        super().__init__()
        self.square = square
        self.color = color
        self.board = board # setup.Board() obj
        self.icon = icon
        self.points = points
        self.code = self.icon[0].upper() if self.color == "White" else self.icon[0]
        
        self.image = pg.transform.rotozoom(
            pg.image.load(f"Pieces/{self.color}/{icon}.png").convert_alpha(), 0, 0.6)
        self.rect = self.image.get_rect(center = self.board.square_dict[self.square].center)

        self.moves = []
        self.pressed = False # Checks if the piece is highlighted by a human player so no other pieces could be clicked on
    
    @abstractmethod
    def possible_moves(self):
        """Abstract method for each piece to generate its own legal moves
        """
        pass                                           

    def play(self, square, pseudo=False):
        """Plays the move chosen by the player and updates the board information

        Args:
            square (pg.rect obj]): the square the piece is to be moved to

        Returns:
            pg.Sprite: returns the captured piece (if one has been captured)
              so the calc.detect_pseudo_moves() func could reverse the action once it's finished calculating.
        """
        removed_sprite = None # retrieve the dead sprite (if there's one) while claculating pseudo moves
        index = list(self.board.square_dict.values()).index(square)
        key = list(self.board.square_dict.keys())[index]
        
        # Captuing a piece
        if key in self.board.occ_squares:
            removed_sprite = self.board.occ_squares[key]   
            self.board.occ_squares[key].kill()  
        
        # Checking for an en passant move, a two-square advance by a pawn and a promotion
        if isinstance(self, Pawn): 
            if abs(int(key[1]) - int(self.square[1])) == 2:  
                self.board.en_passant = f"{key[0]}{int(key[1]) - 1}" if self.color == "White" else f"{key[0]}{int(key[1]) + 1}" 
            else:
                self.board.en_passant = "-"         
            
            if self.square[0] != key[0]:
                if isinstance(self.board.occ_squares.get(f"{key[0]}{self.square[1]}", ""), Pawn):
                    pawn = self.board.occ_squares.get(f"{key[0]}{self.square[1]}", "")
                    if isinstance(self.board.occ_squares.get(f"{key[0]}{self.square[1]}", ""), Pawn):
                        if isinstance(self.board.occ_squares.get(key, ""), str):
                                removed_sprite = pawn
                                self.board.occ_squares.pop(pawn.square)
                                pawn.kill()   
            # Promotion
            if key[1] in ["1", "8"] and pseudo == False:
                inst = Queen(key, self.board, self.color)
                if self.color == "White":
                    self.board.pieces["white"].add(inst)    
                else:
                    self.board.pieces["black"].add(inst)   
                print("test")
                self.kill()
                self.board.occ_squares.pop(self.square)
                self.board.occ_squares[key] = inst
                self.rect.center = self.board.square_dict[self.square].center
                del self       
                return removed_sprite 

        # Castling
        elif isinstance(self, King):
                if pseudo == False:
                    if abs(ord(key[0]) - ord(self.square[0])) == 2:
                        if key[0] > self.square[0]:
                            self.board.occ_squares[f"h{self.square[1]}"].play(self.board.square_dict[f"f{self.square[1]}"])  
                        else:
                            self.board.occ_squares[f"a{self.square[1]}"].play(self.board.square_dict[f"d{self.square[1]}"])   
                    self.moved = True    
                    self.castling["king"] = self.castling["queen"] = "-"       

        elif isinstance(self, Rook) and pseudo == False:
            self.moved = True      
            if self.square[0] == "h":
                if self.color == "White":
                    self.board.w_king.castling["king"] = "-"    
                else:
                    self.board.b_king.castling["king"] = "-"        
            else:
                if self.color == "White":
                    self.board.w_king.castling["queen"] = "-"    
                else:
                    self.board.b_king.castling["queen"] = "-"                            
                               
        
        self.board.occ_squares.pop(self.square)
        self.square = key  
        self.board.occ_squares[key] = self
        self.rect.center = self.board.square_dict[self.square].center

        # castling rights
        if pseudo == False:
            if self.color == "White":
                self.board.w_king.checked = False
            else:
                self.board.b_king.checked = False     

            if self.color == "White":
                if self.board.square_dict[self.board.b_king.square] in self.possible_moves():
                    self.board.b_king.checked = True
            else:
                if self.board.square_dict[self.board.w_king.square] in self.possible_moves():
                    self.board.w_king.checked = True  
        return removed_sprite  

class Pawn(Piece):
    def __init__(self, square: list, board: Any, color: str, icon="pawn", points=1) -> None:
        super().__init__(square, board, color, icon, points)

    def promote(self):
        surface = pg.Surface((self.board.game_surface.get_width / 4, self.board.game_surface.get_height / 4))
        rect = surface.get_rect(center=(self.board.game_surface.get_width / 2, self.board.game_surface.get_height / 2))
        while True:
            surface.fill("#161512")
            self.board.game_surface.blit(surface, rect)
            

    def possible_moves(self):
        super().possible_moves()
        move_list = []
        if self.color == "White":
            # Regular advance
            if f"{self.square[0]}{int(self.square[1]) + 1}" not in self.board.occ_squares:
                if f"{self.square[0]}{int(self.square[1]) + 1}" in self.board.square_dict:
                    move_list.append(self.board.square_dict[f"{self.square[0]}{int(self.square[1]) + 1}"])
                # double-square advance
                if f"{self.square[0]}{int(self.square[1]) + 2}" not in self.board.occ_squares and int(self.square[1]) == 2:
                    if f"{self.square[0]}{int(self.square[1]) + 2}" in self.board.square_dict:
                        move_list.append(self.board.square_dict[f"{self.square[0]}{int(self.square[1]) + 2}"])
            # Regular capture        
            if f"{chr(ord(self.square[0]) + 1)}{int(self.square[1]) + 1}" in self.board.occ_squares:
                if f"{chr(ord(self.square[0]) + 1)}{int(self.square[1]) + 1}" in self.board.square_dict:
                    if self.board.occ_squares[f"{chr(ord(self.square[0]) + 1)}{int(self.square[1]) + 1}"].color != self.color: 
                        move_list.append(self.board.square_dict[f"{chr(ord(self.square[0]) + 1)}{int(self.square[1]) + 1}"])

            if f"{chr(ord(self.square[0]) - 1)}{int(self.square[1]) + 1}" in self.board.occ_squares:
                if f"{chr(ord(self.square[0]) - 1)}{int(self.square[1]) + 1}" in self.board.square_dict:
                    if self.board.occ_squares[f"{chr(ord(self.square[0]) - 1)}{int(self.square[1]) + 1}"].color != self.color: 
                        move_list.append(self.board.square_dict[f"{chr(ord(self.square[0]) - 1)}{int(self.square[1]) + 1}"])    
        else:  
            # Regular advance
            if f"{self.square[0]}{int(self.square[1]) - 1}" not in self.board.occ_squares:
                if f"{self.square[0]}{int(self.square[1]) - 1}" in self.board.square_dict:
                    move_list.append(self.board.square_dict[f"{self.square[0]}{int(self.square[1]) - 1}"])
                # double-square advance
                if f"{self.square[0]}{int(self.square[1]) - 2}" not in self.board.occ_squares and int(self.square[1]) == 7:
                    if f"{self.square[0]}{int(self.square[1]) - 2}" in self.board.square_dict:
                        move_list.append(self.board.square_dict[f"{self.square[0]}{int(self.square[1]) - 2}"]) 
            # Regular capture        
            if f"{chr(ord(self.square[0]) + 1)}{int(self.square[1]) - 1}" in self.board.occ_squares:
                if f"{chr(ord(self.square[0]) + 1)}{int(self.square[1]) - 1}" in self.board.square_dict:
                    if self.board.occ_squares[f"{chr(ord(self.square[0]) + 1)}{int(self.square[1]) - 1}"].color != self.color: 
                        move_list.append(self.board.square_dict[f"{chr(ord(self.square[0]) + 1)}{int(self.square[1]) - 1}"])

            if f"{chr(ord(self.square[0]) - 1)}{int(self.square[1]) - 1}" in self.board.occ_squares:
                if f"{chr(ord(self.square[0]) - 1)}{int(self.square[1]) - 1}" in self.board.square_dict:
                    if self.board.occ_squares[f"{chr(ord(self.square[0]) - 1)}{int(self.square[1]) - 1}"].color != self.color: 
                        move_list.append(self.board.square_dict[f"{chr(ord(self.square[0]) - 1)}{int(self.square[1]) - 1}"])          
        # en passant
        if f"{chr(ord(self.square[0]) + 1)}{self.square[1]}" in self.board.square_dict:
            if isinstance(self.board.occ_squares.get(f"{chr(ord(self.square[0]) + 1)}{self.square[1]}", ""), Pawn):
                pawn = self.board.occ_squares[f"{chr(ord(self.square[0]) + 1)}{self.square[1]}"]
                if pawn.color != self.color:
                    if self.color == "White":
                        move_list.append(self.board.square_dict[f"{chr(ord(self.square[0]) + 1)}{int(self.square[1]) + 1}"])
                    else: 
                        move_list.append(self.board.square_dict[f"{chr(ord(self.square[0]) + 1)}{int(self.square[1]) - 1}"])  
        
        if f"{chr(ord(self.square[0]) - 1)}{self.square[1]}" in self.board.square_dict:
            if isinstance(self.board.occ_squares.get(f"{chr(ord(self.square[0]) - 1)}{self.square[1]}", ""), Pawn):
                pawn = self.board.occ_squares[f"{chr(ord(self.square[0]) - 1)}{self.square[1]}"]
                if pawn.color != self.color:
                    if self.color == "White":
                        move_list.append(self.board.square_dict[f"{chr(ord(self.square[0]) - 1)}{int(self.square[1]) + 1}"])  
                    else: 
                        move_list.append(self.board.square_dict[f"{chr(ord(self.square[0]) - 1)}{int(self.square[1]) - 1}"]) 
                        
        if self.color[0].lower() == self.board.to_move: 
            move_list = calc.detect_pseudo_moves(self, move_list)        
        return move_list                       

class Rook(Piece):
    def __init__(self, square: list, board: Any, color: str, icon="rook", points=5) -> None:
        super().__init__(square, board, color, icon, points)
        self.moved = False # Checks if the rook has been moved as castling condition
    
    def possible_moves(self):
        super().possible_moves()
        moves = calc.horizontal_calc(self)
        moves.extend(calc.vertical_calc(self))
        if self.board.to_move == self.color[0].lower(): 
            moves = calc.detect_pseudo_moves(self, moves)
        return moves
        
class Knight(Piece):
    def __init__(self, square: list, board: Any, color: str, icon="knight", points=3) -> None:
        super().__init__(square, board, color, icon, points)     
        self.code = 'N' if self.color == 'White' else 'n'

    def possible_moves(self):
        super().possible_moves()
        moves = []
        if f"{chr(ord(self.square[0]) + 1)}{int(self.square[1]) + 2}" in self.board.square_dict:
            if f"{chr(ord(self.square[0]) + 1)}{int(self.square[1]) + 2}" not in self.board.occ_squares:
                moves.append(self.board.square_dict[f"{chr(ord(self.square[0]) + 1)}{int(self.square[1]) + 2}"]) 
            
            elif self.board.occ_squares[f"{chr(ord(self.square[0]) + 1)}{int(self.square[1]) + 2}"].color != self.color:
                moves.append(self.board.square_dict[f"{chr(ord(self.square[0]) + 1)}{int(self.square[1]) + 2}"])    

        if f"{chr(ord(self.square[0]) + 1)}{int(self.square[1]) - 2}" in self.board.square_dict:    
            if f"{chr(ord(self.square[0]) + 1)}{int(self.square[1]) - 2}" not in self.board.occ_squares:
                moves.append(self.board.square_dict[f"{chr(ord(self.square[0]) + 1)}{int(self.square[1]) - 2}"]) 
            
            elif self.board.occ_squares[f"{chr(ord(self.square[0]) + 1)}{int(self.square[1]) - 2}"].color != self.color:
                moves.append(self.board.square_dict[f"{chr(ord(self.square[0]) + 1)}{int(self.square[1]) - 2}"])  

        if f"{chr(ord(self.square[0]) - 1)}{int(self.square[1]) - 2}" in self.board.square_dict:    
            if f"{chr(ord(self.square[0]) - 1)}{int(self.square[1]) - 2}" not in self.board.occ_squares:
                moves.append(self.board.square_dict[f"{chr(ord(self.square[0]) - 1)}{int(self.square[1]) - 2}"]) 
            
            elif self.board.occ_squares[f"{chr(ord(self.square[0]) - 1)}{int(self.square[1]) - 2}"].color != self.color:
                moves.append(self.board.square_dict[f"{chr(ord(self.square[0]) - 1)}{int(self.square[1]) - 2}"])   

        if f"{chr(ord(self.square[0]) - 1)}{int(self.square[1]) + 2}" in self.board.square_dict:    
            if f"{chr(ord(self.square[0]) - 1)}{int(self.square[1]) + 2}" not in self.board.occ_squares:
                moves.append(self.board.square_dict[f"{chr(ord(self.square[0]) - 1)}{int(self.square[1]) + 2}"]) 
            
            elif self.board.occ_squares[f"{chr(ord(self.square[0]) - 1)}{int(self.square[1]) + 2}"].color != self.color:
                moves.append(self.board.square_dict[f"{chr(ord(self.square[0]) - 1)}{int(self.square[1]) + 2}"]) 

        if f"{chr(ord(self.square[0]) - 2)}{int(self.square[1]) + 1}" in self.board.square_dict:    
            if f"{chr(ord(self.square[0]) - 2)}{int(self.square[1]) + 1}" not in self.board.occ_squares:
                moves.append(self.board.square_dict[f"{chr(ord(self.square[0]) - 2)}{int(self.square[1]) + 1}"]) 
            
            elif self.board.occ_squares[f"{chr(ord(self.square[0]) - 2)}{int(self.square[1]) + 1}"].color != self.color:
                moves.append(self.board.square_dict[f"{chr(ord(self.square[0]) - 2)}{int(self.square[1]) + 1}"])     

        if f"{chr(ord(self.square[0]) - 2)}{int(self.square[1]) - 1}" in self.board.square_dict:    
            if f"{chr(ord(self.square[0]) - 2)}{int(self.square[1]) - 1}" not in self.board.occ_squares:
                moves.append(self.board.square_dict[f"{chr(ord(self.square[0]) - 2)}{int(self.square[1]) - 1}"]) 
            
            elif self.board.occ_squares[f"{chr(ord(self.square[0]) - 2)}{int(self.square[1]) - 1}"].color != self.color:
                moves.append(self.board.square_dict[f"{chr(ord(self.square[0]) - 2)}{int(self.square[1]) - 1}"])   
        
        if f"{chr(ord(self.square[0]) + 2)}{int(self.square[1]) - 1}" in self.board.square_dict:    
            if f"{chr(ord(self.square[0]) + 2)}{int(self.square[1]) - 1}" not in self.board.occ_squares:
                moves.append(self.board.square_dict[f"{chr(ord(self.square[0]) + 2)}{int(self.square[1]) - 1}"]) 
            
            elif self.board.occ_squares[f"{chr(ord(self.square[0]) + 2)}{int(self.square[1]) - 1}"].color != self.color:
                moves.append(self.board.square_dict[f"{chr(ord(self.square[0]) + 2)}{int(self.square[1]) - 1}"])      

        if f"{chr(ord(self.square[0]) + 2)}{int(self.square[1]) + 1}" in self.board.square_dict:
            if f"{chr(ord(self.square[0]) + 2)}{int(self.square[1]) + 1}" not in self.board.occ_squares:
                moves.append(self.board.square_dict[f"{chr(ord(self.square[0]) + 2)}{int(self.square[1]) + 1}"]) 
            
            elif self.board.occ_squares[f"{chr(ord(self.square[0]) + 2)}{int(self.square[1]) + 1}"].color != self.color:
                moves.append(self.board.square_dict[f"{chr(ord(self.square[0]) + 2)}{int(self.square[1]) + 1}"])                        

        if self.board.to_move == self.color[0].lower(): 
            moves = calc.detect_pseudo_moves(self, moves) 
        return moves               

class Bishop(Piece):
    def __init__(self, square: list, board: Any, color: str, icon="bishop", points=3) -> None:
        super().__init__(square, board, color, icon, points)

    def possible_moves(self):
        super().possible_moves()
        moves = calc.diagonal_calc(self)
        if self.board.to_move == self.color[0].lower(): 
            moves = calc.detect_pseudo_moves(self, moves)
        return moves  

class King(Piece):
    def __init__(self, square: list, board: Any, color: str, icon="king", points=float("inf")) -> None:
        super().__init__(square, board, color, icon, points)
        self.checked = False
        self.castling = {}
        self.moved = False # Checks if the king has moved for castling condition

    def possible_moves(self):
        super().possible_moves()
        moves = []
        if f"{chr(ord(self.square[0]) + 1)}{self.square[1]}" in self.board.square_dict:
            if f"{chr(ord(self.square[0]) + 1)}{self.square[1]}" not in self.board.occ_squares:
                moves.append(self.board.square_dict[f"{chr(ord(self.square[0]) + 1)}{self.square[1]}"])
            
            elif self.board.occ_squares[f"{chr(ord(self.square[0]) + 1)}{self.square[1]}"].color != self.color:  
                moves.append(self.board.square_dict[f"{chr(ord(self.square[0]) + 1)}{self.square[1]}"])  

        if f"{chr(ord(self.square[0]) - 1)}{self.square[1]}" in self.board.square_dict:
            if f"{chr(ord(self.square[0]) - 1)}{self.square[1]}" not in self.board.occ_squares:
                moves.append(self.board.square_dict[f"{chr(ord(self.square[0]) - 1)}{self.square[1]}"])
            
            elif self.board.occ_squares[f"{chr(ord(self.square[0]) - 1)}{self.square[1]}"].color != self.color:  
                moves.append(self.board.square_dict[f"{chr(ord(self.square[0]) - 1)}{self.square[1]}"]) 

        if f"{self.square[0]}{int(self.square[1]) + 1}" in self.board.square_dict:
            if f"{self.square[0]}{int(self.square[1]) + 1}" not in self.board.occ_squares:
                moves.append(self.board.square_dict[f"{self.square[0]}{int(self.square[1]) + 1}"])
            
            elif self.board.occ_squares[f"{self.square[0]}{int(self.square[1]) + 1}"].color != self.color:  
                moves.append(self.board.square_dict[f"{self.square[0]}{int(self.square[1]) + 1}"])    

        if f"{self.square[0]}{int(self.square[1]) - 1}" in self.board.square_dict:
            if f"{self.square[0]}{int(self.square[1]) - 1}" not in self.board.occ_squares:
                moves.append(self.board.square_dict[f"{self.square[0]}{int(self.square[1]) - 1}"])
            
            elif self.board.occ_squares[f"{self.square[0]}{int(self.square[1]) - 1}"].color != self.color:  
                moves.append(self.board.square_dict[f"{self.square[0]}{int(self.square[1]) - 1}"])

        if f"{chr(ord(self.square[0]) - 1)}{int(self.square[1]) + 1}" in self.board.square_dict:
            if f"{chr(ord(self.square[0]) - 1)}{int(self.square[1]) + 1}" not in self.board.occ_squares:
                moves.append(self.board.square_dict[f"{chr(ord(self.square[0]) - 1)}{int(self.square[1]) + 1}"])
            
            elif self.board.occ_squares[f"{chr(ord(self.square[0]) - 1)}{int(self.square[1]) + 1}"].color != self.color:  
                moves.append(self.board.square_dict[f"{chr(ord(self.square[0]) - 1)}{int(self.square[1]) + 1}"])     

        if f"{chr(ord(self.square[0]) - 1)}{int(self.square[1]) - 1}" in self.board.square_dict:
            if f"{chr(ord(self.square[0]) - 1)}{int(self.square[1]) - 1}" not in self.board.occ_squares:
                moves.append(self.board.square_dict[f"{chr(ord(self.square[0]) - 1)}{int(self.square[1]) - 1}"])
            
            elif self.board.occ_squares[f"{chr(ord(self.square[0]) - 1)}{int(self.square[1]) - 1}"].color != self.color:  
                moves.append(self.board.square_dict[f"{chr(ord(self.square[0]) - 1)}{int(self.square[1]) - 1}"])  

        if f"{chr(ord(self.square[0]) + 1)}{int(self.square[1]) - 1}" in self.board.square_dict:
            if f"{chr(ord(self.square[0]) + 1)}{int(self.square[1]) - 1}" not in self.board.occ_squares:
                moves.append(self.board.square_dict[f"{chr(ord(self.square[0]) + 1)}{int(self.square[1]) - 1}"])
            
            elif self.board.occ_squares[f"{chr(ord(self.square[0]) + 1)}{int(self.square[1]) - 1}"].color != self.color:  
                moves.append(self.board.square_dict[f"{chr(ord(self.square[0]) + 1)}{int(self.square[1]) - 1}"])     

        if f"{chr(ord(self.square[0]) + 1)}{int(self.square[1]) + 1}" in self.board.square_dict:
            if f"{chr(ord(self.square[0]) + 1)}{int(self.square[1]) + 1}" not in self.board.occ_squares:
                moves.append(self.board.square_dict[f"{chr(ord(self.square[0]) + 1)}{int(self.square[1]) + 1}"])
            
            elif self.board.occ_squares[f"{chr(ord(self.square[0]) + 1)}{int(self.square[1]) + 1}"].color != self.color:  
                moves.append(self.board.square_dict[f"{chr(ord(self.square[0]) + 1)}{int(self.square[1]) + 1}"])

        # Castle
        if self.checked == False:
            if self.moved == False and (self.castling["king"] != "-" or self.castling["queen"] != "-"): # if king has move and has castling rights
                if self.color == "White":
                    if "h1" in self.board.occ_squares and isinstance(self.board.occ_squares["h1"], Rook):
                        if not self.board.occ_squares["h1"].moved:
                            if "g1" not in self.board.occ_squares and "f1" not in self.board.occ_squares:
                                moves.append(self.board.square_dict["g1"])       
                    
                    if "a1" in self.board.occ_squares and isinstance(self.board.occ_squares["a1"], Rook):  
                        if not self.board.occ_squares["a1"].moved:
                            if "d1" not in self.board.occ_squares and "c1" not in self.board.occ_squares and "b1" not in self.board.occ_squares:
                                moves.append(self.board.square_dict["c1"])  
                else:
                    if "h8" in self.board.occ_squares and isinstance(self.board.occ_squares["h8"], Rook):
                        if not self.board.occ_squares["h8"].moved:
                            if "g8" not in self.board.occ_squares and "f8" not in self.board.occ_squares:
                                moves.append(self.board.square_dict["g8"])         
                    
                    if "a8" in self.board.occ_squares and isinstance(self.board.occ_squares["a8"], Rook):  
                        if not self.board.occ_squares["a8"].moved:
                            if "d8" not in self.board.occ_squares and "c8" not in self.board.occ_squares and "b8" not in self.board.occ_squares:
                                moves.append(self.board.square_dict["c8"])                                                                       

        if self.board.to_move == self.color[0].lower(): 
            moves = calc.detect_pseudo_moves(self, moves)
        return moves                  

class Queen(Piece):
    def __init__(self, square: list, board: Any, color: str, icon="queen", points=9) -> None:
        super().__init__(square, board, color, icon, points)

    def possible_moves(self):  
        super().possible_moves()
        moves = calc.diagonal_calc(self)
        moves.extend(calc.horizontal_calc(self)) 
        moves.extend(calc.vertical_calc(self))  
        if self.board.to_move == self.color[0].lower(): 
            moves = calc.detect_pseudo_moves(self, moves)
        return moves    