import sys
import pygame
from . import game_modes
from .screens import Screens
from .gameplay import GameSystem
from .configLoader import ConfigLoader


class GameEngine:
    def __init__(self) -> None:

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
        self.test_font = pygame.font.Font("font/minecraft.ttf", 50)
        self.test_font.set_bold(True)
        # make it font without test
        self.start_options = Screens().main_menu_screen(
            self.screen, self.width, self.height
        )
        # background = pygame.image.load("photos/main_creen.jpg")

        background_raw = pygame.image.load("photos/main_creen.jpg")

        background = pygame.transform.scale(
            background_raw, (self.width, self.height)
        )
        self.background = background

    def run(self) -> None:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.screen.fill((0, 0, 0))

            if game_modes.state_variable == game_modes.MAIN_MENU_SCREEN:
                self.game_session = None
                self.screen.blit(self.background, (0, 0))
                drawing_copy = self.start_options()
                if drawing_copy["play_game"]:
                    print("PLAY GAME")
                    game_modes.state_variable = game_modes.GAME_SCREEN
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
            elif game_modes.state_variable == game_modes.GAME_SCREEN:
                if not hasattr(self, 'game_session') or not self.game_session:
                    self.game_session = GameSystem(self.screen, self.config)
                x = self.clock.tick(60) / 1000.0
                self.game_session.update(x)
                self.game_session.draw()

            pygame.display.update()
            self.clock.tick(60)
