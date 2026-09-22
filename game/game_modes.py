
class Mod:
    MAIN_MENU_SCREEN = 1
    GAME_SCREEN = 2
    SETTINGS_SCREEN = 3
    HIGHSCORE_SCREEN = 4
    GAME_OVER_SCREEN = 5
    VICTORY_SCREEN = 6
    state_variable: int = MAIN_MENU_SCREEN

    @classmethod
    def updatemod(cls, mod: int) -> None:
        cls.state_variable = mod
