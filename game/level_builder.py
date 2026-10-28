from __future__ import annotations
from typing import TYPE_CHECKING
import random
import pygame
from game.creature.player import movement, Direction
from .creature import Diamond, Netherite
from photos.loderimages import Images
from mazegenerator import MazeGenerator
from .block import Mape, Block

if TYPE_CHECKING:
    from .gameplay import GameSystem


def build_level(game: GameSystem) -> None:
    if game.current_level == 1:
        game.num += 1
        game.seed = game.config.get("seed", 42)
        game.row = 11
        game.column = 7
        game.backimage = game.backphoto[game.current_level + 1]
        game.background = pygame.transform.scale(
            game.backimage,
            (
                Images.width,
                Images.height,
            ),
        )
    else:
        game.num += 1
        game.seed = random.randint(1, 2004)
        if (
            game.num == 3 or game.num == 6 or
            game.num == 9 or game.num == 12
        ):
            game.row += 2
            game.column += 1
        else:
            game.player_creature.player._super_timer -= 2
    maze = MazeGenerator(
        size=(game.row, game.column), seed=game.seed
    )
    game.maze_map = Mape(maze)
    Images._update_size(
        "wall", size=(Block.size * 2.1, Block.size * 1.85)
    )
    game.time_left = game.level_max_time
    movement.traffic_update(Direction.none)

    game.collectibles: list[Diamond | Netherite] = []
    height = len(game.maze_map.every_cell)
    max_y = height - 1
    max_x = len(game.maze_map.every_cell[0]) - 1 if height > 0 else 0
    corners = {
        (1, 1),
        (max_x - 1, 1),
        (1, max_y - 1),
        (max_x - 1, max_y - 1)
    }
    for y, row in enumerate(game.maze_map.coordination_42):
        for x, cell in enumerate(row):
            if not cell:
                if (x, y) in corners:
                    game.collectibles.append(
                        Netherite(Images.screen, game.config, x, y)
                    )
                else:
                    game.collectibles.append(
                        Diamond(Images.screen, game.config, x, y)
                    )
