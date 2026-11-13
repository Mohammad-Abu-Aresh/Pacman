from __future__ import annotations
from functools import lru_cache
import pygame
from .game_modes import Mod

Box = tuple[int, int, int, int]


@lru_cache(maxsize=None)
def _pause_font(size: int) -> pygame.font.Font:
    """
    Create a font for the pause menu texts.
    Cache it because creating a font every frame is expensive.
    made by: Mohammad Abu Aresh
    """
    return pygame.font.SysFont(None, size)


def contains(box: Box, position: tuple[int, int]) -> bool:
    """
    Report whether a screen position is inside a rectangle.
    The rectangle is a tuple of x, y, width and height.
    made by: Mohammad Abu Aresh
    """
    x, y, width, height = box
    return x <= position[0] < x + width and y <= position[1] < y + height


class PauseMenu:
    def __init__(self, width: int, height: int) -> None:
        """
        Create the pause state and the positions of its two buttons.
        Place them in the middle of a screen of the given size.
        made by: Mohammad Abu Aresh
        """
        self.active: bool = False
        self.esc_down: bool = False
        self.mouse_down: bool = True
        self.size: tuple[int, int] = (width, height)
        button_w, button_h = int(width * 0.2), int(height * 0.08)
        left = (width - button_w) // 2
        self.resume_box: Box = (left, int(height * 0.43), button_w, button_h)
        self.menu_box: Box = (left, int(height * 0.55), button_w, button_h)

    def update(self, esc_pressed: bool) -> bool:
        """
        Toggle the pause on a new escape press and handle clicks.
        Return True while the game must stay frozen.
        made by: Mohammad Abu Aresh
        """
        new_press = esc_pressed and not self.esc_down
        self.esc_down = esc_pressed
        if new_press:
            self.active = not self.active
            self.mouse_down = True
            return self.active
        if not self.active:
            return False
        pressed = bool(pygame.mouse.get_pressed()[0])
        clicked = pressed and not self.mouse_down
        self.mouse_down = pressed
        if clicked:
            self._click(pygame.mouse.get_pos())
        return self.active

    def _click(self, position: tuple[int, int]) -> None:
        """
        Run the action of the button under the clicked position.
        Resume the game or return to the main menu.
        made by: Mohammad Abu Aresh
        """
        if contains(self.resume_box, position):
            self.active = False
        elif contains(self.menu_box, position):
            self.active = False
            Mod.updatemod(Mod.MAIN_MENU_SCREEN)

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw the dark overlay, the title and both buttons.
        Highlight the button under the mouse and do nothing when not paused.
        made by: Mohammad Abu Aresh
        """
        if not self.active:
            return
        shade = pygame.Surface(self.size, pygame.SRCALPHA)
        shade.fill((0, 0, 0, 170))
        screen.blit(shade, (0, 0))
        title = _pause_font(120).render("PAUSED", True, (255, 255, 255))
        title_spot = (self.size[0] // 2, int(self.size[1] * 0.3))
        screen.blit(title, title.get_rect(center=title_spot))
        mouse = pygame.mouse.get_pos()
        for box, label in (
            (self.resume_box, "Resume"), (self.menu_box, "Main Menu")
        ):
            color = (95, 95, 95) if contains(box, mouse) else (55, 55, 55)
            pygame.draw.rect(screen, color, pygame.Rect(box))
            pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(box), 3)
            text = _pause_font(48).render(label, True, (255, 255, 255))
            screen.blit(text, text.get_rect(center=pygame.Rect(box).center))
