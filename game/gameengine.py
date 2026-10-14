import sys
from typing import Callable, Dict, Optional
import pygame
from typing import Any
from game.creature.player import Direction, movement
from photos.loderimages import Images
from .game_modes import Mod
from .screens import Screens
from .gameplay import GameSystem


class GameEngine:
    def __init__(self, config: dict[str, Any]) -> None:
        
        # make it str or any to know what screen is this... and rename it
        self.config = config  # config
        pygame.display.set_caption("Pac-Man")
        self.screen = Images.screen
        self.screens = Screens(self.screen, Images.width, Images.height)
        self.start_options: Callable[[], Dict[str, bool]] = (
            self.screens.main_menu_screen()
        )
        self.background = pygame.transform.scale(
            Images.Home, (Images.width, Images.height)
        )
        self.game_session: Optional[GameSystem] = None
        self.settings_callable: Optional[Callable[[], None]] = None
        self.highscore_callable: Optional[Callable[[], None]] = None
        self.loss_callable: Optional[Callable[[], None]] = None
        self.clock = pygame.time.Clock()

    def button_management(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if Mod.state_variable in (
                    Mod.SETTINGS_SCREEN,
                    Mod.VICTORY_SCREEN,
                    Mod.GAME_OVER_SCREEN,
                ):
                    if event.key == pygame.K_BACKSPACE:
                        self.screens.user_text = (
                            self.screens.user_text[:-1]
                        )
                    elif event.key == pygame.K_RETURN:
                        self.screens.addjson(
                            self.screens.user_text, 880,
                            self.config["highscore_filename"]
                            )
                        self.screens.user_text = ""
                        Mod.updatemod(Mod.MAIN_MENU_SCREEN)
                    else:
                        if (
                            len(self.screens.user_text) < 10
                            and event.unicode.isprintable()
                        ):
                            self.screens.user_text += event.unicode
                if event.key == pygame.K_c:
                    if Mod.state_variable == Mod.GAME_SCREEN:
                        self.cheating = not self.cheating
                        print("Cheating:", self.cheating)
                if event.key == pygame.K_RIGHT:
                    move = movement.traffic_update(Direction.right)
                elif event.key == pygame.K_LEFT:
                    move = movement.traffic_update(Direction.left)
                elif event.key == pygame.K_UP:
                    move = movement.traffic_update(Direction.up)
                elif event.key == pygame.K_DOWN:
                    move = movement.traffic_update(Direction.down)
                else:
                    move = None

    def run(self) -> None:
        font = pygame.font.SysFont(None, 36)
        while True:
            fps = self.clock.tick(60)
            self.button_management()
            if Mod.state_variable == Mod.MAIN_MENU_SCREEN:
                self.game_session = None
                self.settings_callable = None
                self.highscore_callable = None
                self.loss_callable = None
                Images.screen.blit(self.background, (0, 0))
                drawing_copy = self.start_options()

                if drawing_copy["play_game"]:
                    print("PLAY GAME")
                    self.cheating = False # The special variable in cheat mode
                    self.hardcore_mode = False
                    Mod.updatemod(Mod.GAME_SCREEN)
                elif drawing_copy["minecraft_mode"]:
                    print("minecraft_mode")
                    self.cheating = False 
                    self.hardcore_mode = True
                    Mod.updatemod(Mod.GAME_SCREEN)
                elif drawing_copy["top scores"]:
                    print("top scores")
                    Mod.updatemod(Mod.HIGHSCORE_SCREEN)
                elif drawing_copy["settings"]:
                    print("SETTINGS")
                    set_screen = Mod.SETTINGS_SCREEN
                    Mod.state_variable = set_screen
                elif drawing_copy["quit_game"]:
                    print("QUIT GAME")
                    pygame.quit()
                    sys.exit(0)
            elif Mod.state_variable == Mod.GAME_SCREEN:

                if not self.game_session:
                    self.game_session = GameSystem(self.config, hardcore_mode=self.hardcore_mode)
                time_tic = fps / 1000.0
                self.game_session.update(time_tic, cheating=self.cheating)
                self.game_session.draw()

                if self.cheating:
                    font_o = font.render("Cheat Mode Activated!", True, (255, 0, 0))

                    Images.screen.blit(font_o, (Images.width - font_o.get_width() - 20, 20))

            elif Mod.state_variable == Mod.SETTINGS_SCREEN:
                if not self.settings_callable:
                    self.settings_callable = self.screens.settings_screen()
                self.settings_callable()
            elif Mod.state_variable == Mod.HIGHSCORE_SCREEN:
                if not self.highscore_callable:
                    self.highscore_callable = self.screens.highscore_screen()
                self.highscore_callable()
            elif Mod.state_variable == Mod.GAME_OVER_SCREEN:
                if not self.loss_callable:
                    self.loss_callable = self.screens.game_over_screen()
                self.loss_callable()
            pygame.display.update()
