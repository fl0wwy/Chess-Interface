from player import *
import piece

tile_size = 100
GAME_SURFACE_SIZE = (8 * tile_size, 8 * tile_size)

class Board():
    def __init__(self, fen, play_as, ai) -> None:
        # display surface of the board
        self.game_surface = pg.Surface(GAME_SURFACE_SIZE)
        self.game_rect = self.game_surface.get_rect(center=((GAME_SURFACE_SIZE[0] / 2) * 1.7, (GAME_SURFACE_SIZE[0] / 2) * 1.2))
        
        
        # board itself
        self.GRID = [[pg.Rect(self.game_rect.left + (x * tile_size) ,self.game_rect.top + (y * tile_size)
                              , tile_size, tile_size) for x in range(8)] for y in range(8)]
        
        # managing pieces
        self.pieces = {"black" : pg.sprite.Group(), "white" : pg.sprite.Group()}
        self.w_king = self.b_king = None
        self.enpassant = "-"
        

        # board conditions
        self.to_move = "w"
        self.board_perspective = "w"
        self.half_moves = 0
        self.full_moves = 1

        # organizing board
        self.square_dict = {}
        self.occ_squares = {}

        self.font = pg.font.Font("pieces/Philosopher-Regular.ttf", 20)

        # player instances and init game state
        self.player_1 = self.player_2 = None
        self.load_fen(fen, play_as, ai)

    def row_col_display(self, display):
        """Displays the board coordinates

        Args:
            display (pg.display obj): Surface to draw the data on
        """
        if self.board_perspective == "w":
            char_x = 97
            for x in reversed(range(8)):
                # row
                rect_x = self.GRID[7][(x -7) * -1].scale_by(0.4, 0.4)
                rect_x.left -= 28
                rect_x.bottom += 47
                display.blit(self.font.render(chr(char_x), True, "#f5f6fa"), rect_x)
                char_x += 1
                # col
                rect_y = self.GRID[(x -7) * -1][7].scale_by(0.4, 0.4)
                rect_y.left += 56
                rect_y.bottom -= 28
                display.blit(self.font.render(str(x + 1), True, "#f5f6fa"), rect_y)
        else:
            char_x = 104
            for x in range(8):
                # row
                rect_x = self.GRID[7][x].scale_by(0.4, 0.4)
                rect_x.left -= 28
                rect_x.bottom += 47
                display.blit(self.font.render(chr(char_x), True, "#f5f6fa"), rect_x)
                char_x -= 1
                # col
                rect_y = self.GRID[x][7].scale_by(0.4, 0.4)
                rect_y.left += 56
                rect_y.bottom -= 28
                display.blit(self.font.render(str(x + 1), True, "#f5f6fa"), rect_y)    

    def display_board(self, display):
        """Colors the board squares

        Args:
            display (pg.displaty obj): Surface to draw on
        """
        DARK_COLOR = "#795548"
        BRIGHT_COLOR = "#A1887F"
        for y in range(8):
            for x in range(8):
                if y % 2 == 0:
                    if x % 2 == 0:
                        pg.draw.rect(display, BRIGHT_COLOR, self.GRID[y][x])
                    else:
                        pg.draw.rect(display, DARK_COLOR, self.GRID[y][x])  
                else:
                    if x % 2 == 0:
                        pg.draw.rect(display, DARK_COLOR, self.GRID[y][x])
                    else:
                        pg.draw.rect(display, BRIGHT_COLOR, self.GRID[y][x]) 
        
        self.row_col_display(display) 

    def flip_board(self):
        if self.board_perspective == "w":
            self.square_dict = self.gen_dict(white_side=False)
            self.board_perspective = "b"
        else:
            self.square_dict = self.gen_dict()      
            self.board_perspective = "w"
        for val in self.pieces.values():
            for piece in val:
                piece.rect.center = self.square_dict[piece.square].center        
    
    def gen_dict(self, white_side=True):
        """Creates a dictionary with the board cord as a key and the pg.rect obj as the value

        Returns:
            dictionary
        """
        dic = {}
        if white_side:
            y_axis = 8
            x_axis = 97 
            for y in range(8):
                for x in range(8):
                    dic[f"{chr(x_axis)}{y_axis}"] = self.GRID[y][x]
                    x_axis += 1
                x_axis = 97    
                y_axis -= 1
            self.board_perspective = "w"    
        else:
            y_axis = 1
            x_axis = 104
            for y in range(8):
                for x in range(8):
                    dic[f"{chr(x_axis)}{y_axis}"] = self.GRID[y][x]
                    x_axis -= 1
                x_axis = 104  
                y_axis += 1 
            self.board_perspective = "b"        
        return dic  

    def load_fen(self, fen, play_as, ai):
        """Reads a fen string and places the pieces on the board accordingly

        Args:
            fen (str): a string format that the function interperates as locations on the board and what piece are to be placed.

        Raises:
            Exception: if the fen string if invalid an exception is raised
        """
        # example fen "7k/3N2qp/b5r1/2p1Q1N1/Pp4PK/7P/1P3p2/6r1 WW"
        pieces = {"r" : piece.Rook, "n" : piece.Knight, "b" : piece.Bishop, "k" : piece.King, 
                  "q" : piece.Queen, "p" : piece.Pawn}

        if fen is None:
            fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

        x = 97
        y = 8

        self.to_move = fen[-12]
        self.player_1 = Human(play_as, self) 
        self.player_2 = AI("b" if play_as == "w" else "w", self) if ai else Human("b" if play_as == "w" else "w", self)
        self.square_dict = self.gen_dict()         
        
        for i in fen[:-13]:
            if i.isdecimal():
                x += int(i)
            elif i.isalpha():
                if i.islower():
                    inst = pieces[i](f"{chr(x)}{y}", self, "Black")
                    self.pieces["black"].add(inst) 
                    self.occ_squares[f"{chr(x)}{y}"] = inst 
                    if i == "k":
                        self.b_king = inst
                else:   
                    inst = pieces[i.lower()](f"{chr(x)}{y}", self, "White")
                    self.pieces["white"].add(inst) 
                    self.occ_squares[f"{chr(x)}{y}"] = inst    
                    if i == "K":
                        self.w_king = inst

                x += 1   
            else:
                y -= 1
                x = 97     

        if fen.count("K") == 2:
            self.w_king.castling["king"] = "K"
        if fen.count("Q") == 2:
            self.w_king.castling["queen"] = "Q"    
        if fen.count("k") == 2:
            self.b_king.castling["king"] = "k"
        if fen.count("q") == 2:
            self.b_king.castling["queen"] = "q"
        
        return fen      

    def gen_fen(self):
        """Generates a fen string from the current board conditions"""
        string = []
        for y in reversed(range(1,9)):
            i = 0
            for x in range(97,105):
                if f"{chr(x)}{y}" in self.occ_squares:  
                    if i != 0:
                        string.append(str(i))
                    string.append(self.occ_squares[f"{chr(x)}{y}"].code)
                    i = 0
                else:
                    i += 1 
            if i != 0:
                string.append(str(i))        
            string.append('/') 
        string.pop(-1)        
        
        castling_rights = [self.w_king.castling["king"], self.w_king.castling["queen"], self.b_king.castling["king"], self.b_king.castling["queen"]]
        string.append(f' {self.to_move} {"".join(castling_rights)} {self.enpassant} {self.half_moves} {self.full_moves}')            
        
        return ''.join(string)  
              
              