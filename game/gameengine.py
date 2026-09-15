import sys
import pygame
from typing import Any
from .screens import Screens
from .gameplay import GameSystem
from .configLoader import ConfigLoader


class GameEngine:
    def __init__(self) -> None:
        self.state_variable: int = Screens.MAIN_MENU_SCREEN
        # make it str or any to know what screen is this... and rename it
        pygame.init()

        self.screen_info = pygame.display.Info()
        self.config = ConfigLoader().load_config
        self.width = self.screen_info.current_w
        self.height = self.screen_info.current_h
        self.screen = pygame.display.set_mode(
            (self.width, self.height)
        )
        pygame.display.set_caption("Pac-Man")
        self.clock = pygame.time.Clock()
        test_font = pygame.font.Font("font/minecraft.ttf", 50)
        test_font.set_bold(True)
        # make it font without test
        self.start_options = Screens().main_menu_screen(
            self.screen, self.width, self.height
        )
        # make the Screen obj sentraliezed what ever the size updated !
        self.title_game = test_font.render("Pac-Man", False, "#7B00FF")
        # background = pygame.image.load("photos/main_creen.jpg")

        background_raw = pygame.image.load("photos/main_creen.jpg")

        background = pygame.transform.scale(
            background_raw, (self.width, self.height)
        )
        self.background = background
        self.game_session: Any = None

    def run(self) -> None:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.screen.fill((0, 0, 0))

            if self.state_variable == Screens.MAIN_MENU_SCREEN:
                self.screen.blit(self.background, (0, 0))
                title_x = (
                    self.screen_info.current_w // 2
                    - self.title_game.get_width() // 2
                )
                self.screen.blit(self.title_game, (title_x, 20))
                drawing_copy = self.start_options()
                if drawing_copy["play_game"]:
                    print("PLAY GAME")
                    self.state_variable = Screens.GAME_SCREEN
                elif drawing_copy["minecraft_mode"]:
                    print("minecraft_mode")
                elif drawing_copy["top scores"]:
                    print("top scores")
                    self.state_variable = 4
                elif drawing_copy["settings"]:
                    print("SETTINGS")
                    self.state_variable = 3
                elif drawing_copy["quit_game"]:
                    print("QUIT GAME")
                    pygame.quit()
                    sys.exit(0)
            elif self.state_variable == Screens.GAME_SCREEN:
                if not self.game_session:
                    self.game_session = GameSystem(self.screen, self.config)
                self.game_session.update()
                self.game_session.draw()

            pygame.display.update()
            self.clock.tick(60)
