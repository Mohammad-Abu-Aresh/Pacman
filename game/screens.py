from typing import Callable
import pygame


class Button:
    def __init__(
        self,
        coordinates: tuple[int, int],
        text: str,
        font_size: int,
    ) -> None:
        self.x = coordinates[0]
        self.y = coordinates[1]
        self.text = text
        self.font_size = font_size
        self.rect = pygame.Rect(
            self.x - 100, self.y - 25, 200, 50
        )
        self.clicked = False

    def draw(self, screen: pygame.Surface) -> bool:
        action = False
        button_font = pygame.font.Font(
            "font/minecraft.ttf", self.font_size
        )
        button_text = button_font.render(
            self.text, False, "#000000"
        )
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if (
                pygame.mouse.get_pressed()[0]
                and not self.clicked
            ):
                self.clicked = True
                action = True
                print('CLICKED')
        else:
            self.clicked = False
        screen.blit(
            button_text,
            (
                self.x - button_text.get_width() // 2,
                self.y - button_text.get_height() // 2,
            ),
        )

        return action


class Screens:

    def start_screen(
        self, screen: pygame.Surface, width: int
    ) -> Callable[[], dict[str, bool]]:
        bly_now = Button(
            (width // 2, 200), "Bly Now", 30
        )
        best_players = Button(
            (width // 2, 300), "Best Players", 30
        )
        exit_game = Button(
            (width // 2, 400), "Exit Game", 30
        )

        def draw_buttons() -> dict[str, bool]:
            return {
                "bly_now": bly_now.draw(screen),
                "best_players": best_players.draw(screen),
                "exit_game": exit_game.draw(screen),
            }
        return draw_buttons
