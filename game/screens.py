from typing import Callable, Optional
import pygame


class Button:

    def __init__(
        self,
        coordinates: tuple[int, int],
        size: tuple[int, int],
        text: Optional[str] = None,
        font_size: int = 25,
        text_color: str | tuple[int, int, int] = "#000000",

    ) -> None:
        self.x = coordinates[0]
        self.y = coordinates[1]
        self.text = text
        self.font_size = font_size
        self.text_color = text_color
        self.rect = pygame.Rect(
            self.x - size[0] // 2, self.y - size[1] // 2, size[0], size[1]
        )
        self.clicked = False

    def draw(self, screen: pygame.Surface) -> bool:
        action = False
        button_font = pygame.font.Font(
            "font/minecraft.ttf", self.font_size
        )
        button_text = button_font.render(
            self.text if self.text is not None else "", False, self.text_color
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
                self.x - button_text.get_width(),
                self.y - button_text.get_height(),
            ),
        )

        return action


class Screens:

    def main_menu_screen(
        self, screen: pygame.Surface, width: int,
        height: int
    ) -> Callable[[], dict[str, bool]]:
        play_game = Button(
            (int(width * 0.21), int(height * 0.41)),
            (int(width * 0.22), int(height * 0.08))
        )
        minecraft_mode = Button(
            (int(width * 0.21), int(height * 0.51)),
            (int(width * 0.22), int(height * 0.08))
        )
        achievements = Button(
            (int(width * 0.21), int(height * 0.60)),
            (int(width * 0.22), int(height * 0.08))
        )
        settings = Button(
            (int(width * 0.21), int(height * 0.69)),
            (int(width * 0.22), int(height * 0.08))
        )
        quit_game = Button(
            (int(width * 0.21), int(height * 0.78)),
            (int(width * 0.22), int(height * 0.08))
        )

        def draw_buttons() -> dict[str, bool]:
            return {
                "play_game": play_game.draw(screen),
                "minecraft_mode": minecraft_mode.draw(screen),
                "top scores": achievements.draw(screen),
                "settings": settings.draw(screen),
                "quit_game": quit_game.draw(screen),
            }
        return draw_buttons
