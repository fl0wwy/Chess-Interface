from setup import *
import pyperclip
import os

class Game():
    """Game class which houses all window functions and game loop
    """
    def __init__(self, fen : str, play_as : str, ai: bool, depth=10) -> None:
        """Initialization of the game

        Args:
            fen (str): FEN string to generate the game position
            play_as (str): "w" or "b" determines which side the human/main player plays on
            ai (bool): True if players wants to play vs AI else False
            depth (int, optional): AI Move calculation depth. Defaults to 10.
        """
        pg.init()
        self.display = pg.display.set_mode((800 * 1.7, 800 * 1.2))
        self.clock = pg.time.Clock()

        pg.display.set_caption("Chess")
        pg.display.set_icon(pg.transform.rotozoom(
            pg.image.load("Pieces/White/knight.png").convert_alpha(), 0, 0.2))
        
        self.font = pg.font.Font("pieces/Philosopher-Regular.ttf", 30)
        self.board = Board(fen, play_as, ai, depth) # initializing the game
        self.ai = ai

        if play_as == "b":
            self.board.flip_board()

    def update(self):
        pg.display.update()
        self.clock.tick(60)
        #pg.display.set_caption(str(round(self.clock.get_fps(),2))) # Test for lag

    def check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            
            if event.type == pg.KEYDOWN: 
                if pg.key.get_pressed()[pg.K_SPACE]:
                    self.board.flip_board()  
                
                if pg.key.get_pressed()[pg.K_DOWN] & self.board.running:
                    self.traverse_positions(-1)  
                
                if pg.key.get_pressed()[pg.K_UP] & self.board.running:  
                    self.traverse_positions(1)   
                
                if pg.key.get_pressed()[pg.K_LCTRL] & pg.key.get_pressed()[pg.K_MINUS] & self.board.running:  
                    self.resize_window(-10)      
                
                if pg.key.get_pressed()[pg.K_LCTRL] & pg.key.get_pressed()[pg.K_EQUALS] & self.board.running: 
                    self.resize_window(10)         
    
    def resize_window(self, increment : int):
        """Resizing the window by an increment each time a certain keydown event occurs

        Args:
            increment (int): determines by how much the size of each board square should increase/decrease

        Returns:
            False if the window size > 0
        """
        if self.board.tile_size + increment <= 0:
            return False
        
        temp = self.board
        
        self.board = Board(self.board.current_fen, play_as=temp.player_1.color, ai=ai, depth=temp.ai_depth, tile_size=temp.tile_size + increment)
        self.board.game_positions = temp.game_positions
        self.board.game_position_index = temp.game_position_index
        self.display = pg.display.set_mode((self.board.GAME_SURFACE_SIZE * 1.7, self.board.GAME_SURFACE_SIZE * 1.2))
        self.font = pg.font.Font("pieces/Philosopher-Regular.ttf", int(30 * (self.board.tile_size/100)))
    
    def traverse_positions(self, increment : int):
        """Traverse throughout all positions played in game so far.

        Args:
            increment (int): by how many moves should the function jump back and forth from

        Returns:
           False if the move index doesn't exist
        """
        if self.board.game_position_index + increment > -1:
            return False
        if self.board.game_position_index + increment < len(self.board.game_positions) * -1:
            return False 
        self.board.game_position_index += increment  
        
        self.board.reset_board()
        self.board.load_fen(self.board.game_positions[self.board.game_position_index], self.board.player_1.color, self.ai)
        self.board.current_fen = self.board.gen_fen()
        self.board.position_analysis = self.board.analyze_position(self.board.current_fen, self.board.ai_depth)[1]
    
    def display_fen(self):
        """Displays the FEN string of the current position
        """
        text = self.font.render(f"FEN(click to copy): {self.board.current_fen}", True, "white")
        rect = text.get_rect(center = (self.display.get_width() / 2, (self.display.get_height() -(50 * (self.board.tile_size/100)))))
        self.display.blit(text, rect)    
        if rect.collidepoint(pg.mouse.get_pos()):
            if pg.mouse.get_pressed()[0]:
                pyperclip.copy(self.board.current_fen)   

    def display_eval(self):
        """Displays Stockfish's evaluation of the current position"""
        text = self.font.render(f"Stockfish eval: {self.board.position_analysis}", True, "white")
        rect = text.get_rect(center = ((self.display.get_width() -(140 * (self.board.tile_size/100))), self.display.get_height() / 2))
        self.display.blit(text, rect)    
        if rect.collidepoint(pg.mouse.get_pos()):
            if pg.mouse.get_pressed()[0]:
                pyperclip.copy(self.board.current_fen)             

    def game_over_message(self):
        """Display the game_over state once the game has concluded (checkmate or stalemate)
        """
        if self.board.game_over(self.board.current_fen) == 1:
            if self.board.to_move == "w":
                text = self.font.render(f"Checkmate. White wins.", True, "White")
            else:
                text = self.font.render(f"Checkmate. White wins.", True, "White")    
        else:
            text = self.font.render(f"Stalemate.", True, "White")   

        rect = text.get_rect(center=(self.display.get_width() / 2, self.display.get_height() - ((self.display.get_height() - 40 * (self.board.tile_size/100)))))    
        self.display.blit(text, rect)            
    
    def __call__(self):
        """Game loop
        """
        while True:
            self.display.fill("#161512")
            self.check_events()
            
            self.board.display_board(self.display)
            if self.board.player_1.color == "b":
                self.board.pieces["white"].draw(self.display)
                self.board.pieces["black"].draw(self.display) 
            else:
                self.board.pieces["black"].draw(self.display)
                self.board.pieces["white"].draw(self.display)  
            self.board.pieces["black"].update()
            self.board.pieces["white"].update()    
            
            if self.board.running:  
                self.board.player_1.move(self.display)
                self.board.player_2.move() if self.ai else self.board.player_2.move(self.display)
            else:
                self.game_over_message()
            
            if os.path.exists("./stockfish") and os.path.isdir("./stockfish"):
                self.display_eval()
            
            self.display_fen()  
            self.update()

if __name__ == "__main__":
    """Inputs about the game settings and calling the game loop function
    """
    start_fen = input('Enter your customized fen string or to start a new game type "new": ')
    if start_fen.lower() == "new":
        start_fen = None
    
    play_as = input("Play as white or black? [w/b] (defaults to white): ")
    if play_as.lower() not in ["W", "b"]:
        play_as = "w"    
    
    ai = input("Play vs AI? [y/n]: ")
    ai = True if ai.lower() == "y" else False
    
    difficulty = input("choose a difficulty to play against (easy, moderate, hard): ") if ai == True else 10
    if difficulty != 10:
        if difficulty.lower() not in ["easy", "moderate", "hard"]:
            difficulty = 10
        else:
            if difficulty.lower() == "easy":
                difficulty = 2
            elif difficulty.lower() == "moderate":
                difficulty = 5
            else:
                difficulty = 10           
    
    print("press SPACEBAR to flip the board, ARROWS UP/DOWN to traverse moves, CTRL +/- to zoom.")
    
    game = Game(start_fen, play_as, ai, difficulty)
    game()