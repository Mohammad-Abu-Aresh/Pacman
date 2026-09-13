import sys
import pygame
from .screens import Screens


class GameEngine:
    def __init__(self) -> None:
        self.state_variable: int = Screens.MAIN_MENU_SCREEN
        # make it str or any to know what screen is this... and rename it
        pygame.init()

        self.screen_info = pygame.display.Info()
        width = self.screen_info.current_w
        height = self.screen_info.current_h

        self.screen = pygame.display.set_mode(
            (width, height)
        )
        pygame.display.set_caption("Pac-Man")
        self.clock = pygame.time.Clock()
        test_font = pygame.font.Font("font/minecraft.ttf", 50)
        test_font.set_bold(True)
        # make it font without test
        self.start_options = Screens().MAIN_MENU_SCREEN(
                self.screen, width, height
                )
        # make the Screen obj sentraliezed what ever the size updated !
        self.title_game = test_font.render("Pac-Man", False, "#7B00FF")
        # background = pygame.image.load("photos/main_creen.jpg")

        background_raw = pygame.image.load("photos/main_creen.jpg")

        background = pygame.transform.scale(background_raw, (width, height))
        self.background = background

    def run(self) -> None:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.screen.fill((0, 0, 0))

            if self.state_variable == Screens.MAIN_MENU_SCREEN:
                self.screen.blit(self.background, (0, 0))
                title_x = self.screen_info.current_w // 2 - self.title_game.get_width() // 2
                self.screen.blit(self.title_game, (title_x, 20))
                drawing_copy = self.start_options()
                if drawing_copy["play_game"]:
                    print("PLAY GAME")
                    # self.state_variable = 2
                elif drawing_copy["minecraft_mode"]:
                    print("minecraft_mode")
                elif drawing_copy["top scores"]:
                    print("top scores")
                    # self.state_variable = 4
                elif drawing_copy["settings"]:
                    print("SETTINGS")
                    # self.state_variable = 3
                elif drawing_copy["quit_game"]:
                    print("QUIT GAME")
                    # pygame.quit()
                    # sys.exit(0)

            pygame.display.update()
            self.clock.tick(60)

        def update_game_time() -> None:
            pass

        def toggle_cheat_mode() -> None:
            pass
