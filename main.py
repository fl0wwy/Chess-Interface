from setup import *
import pyperclip
import os

class Game():
    def __init__(self, fen, play_as, ai, depth=10) -> None:
        pg.init()
        self.display = pg.display.set_mode((GAME_SURFACE_SIZE[0] * 1.7, GAME_SURFACE_SIZE[0] * 1.2))
        self.clock = pg.time.Clock()

        pg.display.set_caption("Chess")
        pg.display.set_icon(pg.transform.rotozoom(
            pg.image.load("Pieces/White/knight.png").convert_alpha(), 0, 0.2))
        
        self.font = pg.font.Font("pieces/Philosopher-Regular.ttf", 30)
        self.board = Board(fen, play_as, ai, depth)
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
            if event.type == pg.KEYDOWN and pg.key.get_pressed()[pg.K_SPACE]:
                self.board.flip_board()   
   
            # if event.type == pg.KEYDOWN and pg.key.get_pressed()[pg.K_ESCAPE] and not self.start_menu:
            #     if self.esc_menu == False:
            #         self.esc_menu = True
            #         self.game_active = False    
            #     else:
            #         self.esc_menu = False
            #         self.game_active = True

    def display_fen(self):
        text = self.font.render(f"FEN(click to copy): {self.board.current_fen}", True, "white")
        rect = text.get_rect(center = (self.display.get_width() / 2, self.display.get_height() - 50))
        self.display.blit(text, rect)    
        if rect.collidepoint(pg.mouse.get_pos()):
            if pg.mouse.get_pressed()[0]:
                pyperclip.copy(self.board.current_fen)   

    def display_eval(self):
            text = self.font.render(f"Stockfish eval: {self.board.position_analysis}", True, "white")
            rect = text.get_rect(center = (self.display.get_width() -140, self.display.get_height() / 2))
            self.display.blit(text, rect)    
            if rect.collidepoint(pg.mouse.get_pos()):
                if pg.mouse.get_pressed()[0]:
                    pyperclip.copy(self.board.current_fen)             

    def __call__(self):
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
            self.board.player_1.move(self.display)
            self.board.player_2.move() if self.ai else self.board.player_2.move(self.display)
            
            # if self.board.check_winner() is not None:
            #     if self.board.check_winner() == -1:
            #         render = self.font.render("Checkmate, Black is victorious.", True, "#f5f6fa")
            #     elif self.board.check_winner() == 1:    
            #         render = self.font.render("Checkmate, White is victorious.", True, "#f5f6fa")
            #     else:
            #         render = self.font.render("Draw.", True, "white")  
            #     rect = render.get_rect(center = (GAME_WINDOW_SIZE[0] / 2, GAME_WINDOW_SIZE[0] / 2)) 
            #     self.display.blit(render,rect)     

            if os.path.exists("./stockfish") and os.path.isdir("./stockfish"):
                self.display_eval()
            
            self.display_fen()    
            self.update()

if __name__ == "__main__":
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
    
    Game(start_fen, play_as, ai, difficulty)()
