import sys
from typing import Any, Callable, Dict, Optional
import pygame
from .game_modes import Mod
from .screens import Screens
from .gameplay import GameSystem
from .configLoader import ConfigLoader


class GameEngine:
    def __init__(self) -> None:
        pygame.init()
        self.screen_info: pygame.display.Info = pygame.display.Info()
        self.config: Dict[str, Any] = ConfigLoader().load_config
        self.width: int = self.screen_info.current_w
        self.height: int = self.screen_info.current_h
        self.screen: pygame.Surface = pygame.display.set_mode(
            (self.width, self.height)
        )
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.test_font: pygame.font.Font = pygame.font.Font(None, 50)
        self.test_font.set_bold(True)
        self.screens: Screens = Screens(
            self.screen, self.width, self.height
        )
        self.start_options: Callable[[], Dict[str, bool]] = (
            self.screens.main_menu_screen()
        )

        background_raw: pygame.Surface = pygame.image.load(
            "photos/screens/main_creen.jpg"
        )
        background: pygame.Surface = pygame.transform.scale(
            background_raw, (self.width, self.height)
        )
        self.background: pygame.Surface = background
        self.game_session: Optional[Any] = None
        self.highscore: Optional[Callable[[], None]] = None
        self.loss: Optional[Callable[[], None]] = None

    def run(self) -> None:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if Mod.state_variable in (
                        Mod.SETTINGS_SCREEN,
                        Mod.VICTORY_SCREEN,
                        Mod.GAME_OVER_SCREEN
                    ):
                        if event.key == pygame.K_BACKSPACE:
                            self.screens.user_text = (
                                self.screens.user_text[:-1]
                            )
                        elif event.key == pygame.K_RETURN:
                            self.screens.user_text = ''
                            Mod.updatemod(Mod.MAIN_MENU_SCREEN)
                        else:
                            if (
                                len(self.screens.user_text) < 10
                                and event.unicode.isprintable()
                            ):
                                self.screens.user_text += event.unicode

            if Mod.state_variable == Mod.MAIN_MENU_SCREEN:
                self.game_session = None
                self.screen.blit(self.background, (0, 0))
                drawing_copy: Dict[str, bool] = self.start_options()
                if drawing_copy["play_game"]:
                    print("PLAY GAME")
                    Mod.updatemod(Mod.GAME_SCREEN)
                elif drawing_copy["minecraft_mode"]:
                    print("minecraft_mode")
                elif drawing_copy["top scores"]:
                    print("top scores")
                    Mod.updatemod(Mod.HIGHSCORE_SCREEN)
                elif drawing_copy["settings"]:
                    print("SETTINGS")
                    Mod.state_variable = Mod.SETTINGS_SCREEN
                elif drawing_copy["quit_game"]:
                    print("QUIT GAME")
                    pygame.quit()
                    sys.exit(0)
            elif Mod.state_variable == Mod.GAME_SCREEN:
                if not self.game_session:
                    self.game_session = GameSystem(
                        self.screen, self.config
                    )
                x: float = self.clock.tick(60) / 1000.0
                self.game_session.update(x)
                self.game_session.draw()
            elif Mod.state_variable == Mod.SETTINGS_SCREEN:
                if not self.game_session:
                    self.game_session = self.screens.settings_screen()
                self.game_session()
            elif Mod.state_variable == Mod.HIGHSCORE_SCREEN:
                if not self.highscore:
                    self.highscore = self.screens.highscore_screen()
                self.highscore()
            elif Mod.state_variable == Mod.GAME_OVER_SCREEN:
                if not self.loss:
                    self.loss = self.screens.game_over_screen()
                self.loss()

            pygame.display.update()
