from __future__ import annotations
from functools import lru_cache
from typing import TYPE_CHECKING
import pygame
from photos.loderimages import Images
from .block import Block
from .overlay import make_shade, maze_backdrop_box

BACKDROP_OPACITY = 0.7

if TYPE_CHECKING:
    from .creature.abilities import Arrow
    from .creature.creature import Creature
    from .gameplay import GameSystem


@lru_cache(maxsize=4)
def _backdrop_shade(size: tuple[int, int]) -> pygame.Surface:
    """
    Create the translucent black surface of the maze backdrop.
    Cache it by size because building a surface each frame is slow.
    made by: Mohammad Abu Aresh
    """
    return make_shade(size, BACKDROP_OPACITY)


def draw_backdrop(game: GameSystem) -> None:
    """
    Fill the area behind the maze with translucent black.
    Cover the wall footprint and let a faint trace of the level show.
    made by: Mohammad Abu Aresh
    """
    mape = game.maze_map
    left, top, width, height = maze_backdrop_box(
        len(mape.every_cell), len(mape.every_cell[0]),
        (mape.origin_x, mape.origin_y), Block.size,
    )
    Images.screen.blit(_backdrop_shade((width, height)), (left, top))


def reveal_clip(game: GameSystem, progress: float) -> pygame.Rect | None:
    """
    Return the screen area of the maze that is already revealed.
    Wipe the maze downward and return None once it is fully shown.
    made by: Mohammad Abu Aresh
    """
    if progress >= 1.0:
        return None
    mape = game.maze_map
    total = (len(mape.every_cell) + 1) * Block.size
    return pygame.Rect(0, mape.origin_y, Images.width, int(total * progress))


def draw_maze_layer(game: GameSystem) -> None:
    """
    Draw the backdrop, walls, gums and creatures of the maze.
    Respect the level intro so only the spawned parts are visible.
    made by: Mohammad Abu Aresh
    """
    intro = game.intro
    progress = intro.maze_progress()
    if progress <= 0:
        return
    Images.screen.set_clip(reveal_clip(game, progress))
    draw_backdrop(game)
    mobs = game.mobs[: intro.visible_actor_count(len(game.mobs))]
    actors: list[Creature | Arrow] = [
        *mobs, *game.player_creature.Skeleton.active_arrows
    ]
    shown = intro.visible_collectible_count(len(game.collectibles))
    game.world_renderer.draw(game.maze_map, actors, game.collectibles[:shown])
    Images.screen.set_clip(None)


@lru_cache(maxsize=None)
def _countdown_font(size: int) -> pygame.font.Font:
    """
    Create the large font used by the countdown numbers.
    Cache it because creating a font every frame is expensive.
    made by: Mohammad Abu Aresh
    """
    return pygame.font.SysFont(None, size)


def draw_countdown(game: GameSystem) -> None:
    """
    Draw the big 3, 2, 1 countdown in the middle of the screen.
    Shrink each number during its second with a dark shadow behind.
    made by: Mohammad Abu Aresh
    """
    number = game.intro.countdown_number()
    if number is None:
        return
    scale = 1.0 + 0.5 * (1.0 - game.intro.countdown_fraction())
    font = _countdown_font(320)
    center = Images.screen.get_rect().center
    for color, offset in (((0, 0, 0), 8), ((255, 255, 255), 0)):
        text = pygame.transform.rotozoom(
            font.render(str(number), True, color), 0, scale
        )
        spot = (center[0] + offset, center[1] + offset)
        Images.screen.blit(text, text.get_rect(center=spot))
