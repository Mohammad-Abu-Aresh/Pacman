import sys
import pygame
from .screens import Screens


class GameEngine:

    def run(self) -> None:
        state_variable: int = 1
        pygame.init()
        height = 600
        width = 800
        screen = pygame.display.set_mode(
            (width, height), pygame.RESIZABLE
        )
        pygame.display.set_caption("Pac-Man")
        clock = pygame.time.Clock()
        test_font = pygame.font.Font("font/minecraft.ttf", 50)
        start_options = Screens().start_screen(screen, width)
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
                if drawing_copy["bly_now"]:
                    print("BLY NOW")
                    state_variable = 2
                elif drawing_copy["best_players"]:
                    print("BEST PLAYERS")
                    state_variable = 3
                elif drawing_copy["exit_game"]:
                    print("EXIT GAME")
                    pygame.quit()
                    sys.exit()
            pygame.display.update()
            clock.tick(60)

        def handle_events() -> None:
            pass

        def update_game_time() -> None:
            pass

        def toggle_cheat_mode() -> None:
            pass
