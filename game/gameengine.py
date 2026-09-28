import sys
import pygame
from photos.loderimages import Images
from .game_modes import Mod
from .screens import Screens
from .gameplay import GameSystem
from .configLoader import ConfigLoader


class GameEngine:
    def __init__(self) -> None:

        # make it str or any to know what screen is this... and rename it
        self.screen_info = pygame.display.Info()
        self.config = ConfigLoader().load_config
        pygame.display.set_caption("Pac-Man")
        self.test_font = pygame.font.Font(None, 50)
        # self.test_font.set_bold(True)
        # make it font without test
        self.start_options = Screens().main_menu_screen(
            Images.screen, Images.width, Images.height
        )

        self.background = pygame.transform.scale(
            Images.Home, (Images.width, Images.height)
        )

    def run(self) -> None:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if Mod.state_variable == Mod.MAIN_MENU_SCREEN:
                self.game_session = None
                Images.screen.blit(self.background, (0, 0))
                drawing_copy = self.start_options()
                if drawing_copy["play_game"]:
                    self.clock = pygame.time.Clock()
                    print("PLAY GAME")
                    Mod.updatemod(Mod.GAME_SCREEN)
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
            elif Mod.state_variable == Mod.GAME_SCREEN:
                if not hasattr(self, 'game_session') or not self.game_session:
                    self.game_session = GameSystem(self.config)
                x = self.clock.tick(60) / 1000.0
                self.game_session.update(x)
                self.game_session.draw()

            pygame.display.update()
