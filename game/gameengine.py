import sys
import pygame
from .screens import Screens


class GameEngine:

    def run(self) -> None:
        state_variable: int = 1 
        # make it str or any to know what screen is this... and rename it
        pygame.init()

        screen_info = pygame.display.Info()
        width = screen_info.current_w
        height = screen_info.current_h

        screen = pygame.display.set_mode(
            (width, height), pygame.RESIZABLE
        )
        pygame.display.set_caption("Pac-Man")
        clock = pygame.time.Clock()
        test_font = pygame.font.Font("font/minecraft.ttf", 50)
        test_font.set_bold(True)
        # make it font without test
        start_options = Screens().start_screen(screen, width)
        # make the Screen obj sentraliezed what ever the size updated !
        title_game = test_font.render("Pac-Man", False, "#7B00FF")
        background = pygame.image.load("photos/kjf.png")

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            screen.blit(background, (0, 0))
            title_x = width // 2 - title_game.get_width() // 2
            screen.blit(title_game, (title_x, 20))

            if state_variable == 1:
                drawing_copy = start_options()
                if drawing_copy["play_now"]:
                    print("PLAY NOW")
                    state_variable = 2
                elif drawing_copy["best_players"]:
                    print("BEST PLAYERS")
                    state_variable = 3
                elif drawing_copy["exit_game"]:
                    print("EXIT GAME")
                    pygame.quit()
                    sys.exit(0)
            pygame.display.update()
            clock.tick(90)

        def handle_events() -> None:
            pass

        def update_game_time() -> None:
            pass

        def toggle_cheat_mode() -> None:
            pass
