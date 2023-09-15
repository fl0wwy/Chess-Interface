from setup import *

class Game():
    def __init__(self) -> None:
        pg.init()
        self.display = pg.display.set_mode((GAME_SURFACE_SIZE[0] * 1.7, GAME_SURFACE_SIZE[0] * 1.2))
        self.clock = pg.time.Clock()

        pg.display.set_caption("Chess")
        pg.display.set_icon(pg.transform.rotozoom(
            pg.image.load("Pieces/White/knight.png").convert_alpha(), 0, 0.2))
        
        self.font = pg.font.Font("pieces/Philosopher-Regular.ttf", 30)
        self.board = Board(None, "w", False)

        self.ai = False

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
        text = self.font.render(self.board.gen_fen(), True, "white")
        rect = text.get_rect(center = (self.display.get_width() / 2, self.display.get_height() - 50))
        self.display.blit(text, rect)       

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

            self.display_fen()
            self.update()

if __name__ == "__main__":
    # start_fen = input("Enter your customized fen string or to start a normal game enter [w/b]: ")
    # ai = input("Play vs AI? [y/n]: ")
    # ai = True if ai.lower() == "y" else False
    Game()()
