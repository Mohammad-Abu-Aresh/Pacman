from __future__ import annotations
import pygame

Box = tuple[int, int, int, int]


def opacity_to_alpha(opacity: float) -> int:
    """
    Convert an opacity from zero to one to a pygame alpha value.
    Clamp the opacity so the alpha always stays between 0 and 255.
    made by: Mohammad Abu Aresh
    """
    return round(255 * min(max(opacity, 0.0), 1.0))


def make_shade(size: tuple[int, int], opacity: float) -> pygame.Surface:
    """
    Create a black translucent surface of the given size.
    Use the opacity where 0 is invisible and 1 is solid black.
    made by: Mohammad Abu Aresh
    """
    shade = pygame.Surface(size, pygame.SRCALPHA)
    shade.fill((0, 0, 0, opacity_to_alpha(opacity)))
    return shade


def names_panel_box(
    widths: list[int], center_x: int, start_y: int, row_gap: int
) -> Box | None:
    """
    Compute the rectangle that sits behind a column of centered names.
    Return None when there are no names so nothing is drawn.
    made by: Mohammad Abu Aresh
    """
    if not widths:
        return None
    margin = 30
    width = max(widths) + margin * 2
    height = len(widths) * row_gap + margin
    top = start_y - row_gap // 2 - margin // 2
    return center_x - width // 2, top, width, height


def maze_backdrop_box(
    rows: int, columns: int, origin: tuple[float, float], block: int
) -> Box:
    """
    Compute the screen rectangle covered by the maze backdrop.
    Match the footprint of the wall images drawn for the maze.
    made by: Mohammad Abu Aresh
    """
    left = int(origin[0] + block * 0.55)
    top = int(origin[1] + block * 0.38)
    return left, top, columns * block, int((rows + 0.2) * block)
