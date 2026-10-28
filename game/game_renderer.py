from __future__ import annotations
from typing import TYPE_CHECKING
import pygame
from photos.loderimages import Images
from .block import Block

if TYPE_CHECKING:
    from .gameplay import GameSystem


def draw_game(game: GameSystem) -> None:
    draw_maze(game, game.maze_map.origin_x, game.maze_map.origin_y)
    for item in game.collectibles:
        item.draw(game.maze_map)
    for mob in sorted(
        game.mobs,
        key=lambda mob: int(mob.y + 0.5)
    ):
        mob.draw(game.maze_map)
    draw_hud(game)


def draw_maze(game: GameSystem, origin_x: int, origin_y: int) -> None:
    maze_bool = game.maze_map.every_cell
    cell_size = Block.size
    for item in game.collectibles:
        item.draw(game.maze_map)

    Images.screen.blit(game.background, (0, 0))
    for y, row in enumerate(maze_bool):
        for x, cell in enumerate(row):
            location_x = origin_x + (x * cell_size)
            location_y = origin_y + (y * cell_size)
            if cell:
                Images._drow(
                    Images.wall_new,
                    location=(location_x, location_y)
                )
            else:
                continue


def draw_hud(game: GameSystem) -> None:
    panel_x = 1480
    panel_y = 100
    spacing_y = 50
    draw_timer(game, panel_x, panel_y)
    draw_score(game, panel_x, panel_y + spacing_y)
    draw_heart(game, panel_x, panel_y + (spacing_y * 2))


def draw_timer(game: GameSystem, x: int, y: int) -> None:
    shadow_surface = game.font.render(
        f"Time: {int(game.time_left)}", True, (0, 0, 0)
    )
    Images.screen.blit(shadow_surface, (x + 2, y + 2))
    text_surface = game.font.render(
        f"Time: {int(game.time_left)}", True, (255, 255, 255)
    )
    Images.screen.blit(text_surface, (x, y))


def draw_score(game: GameSystem, x: int, y: int) -> None:
    score = game.player_creature.player.score
    shadow_surface = game.font.render(
        f"Score: {score}", True, (0, 0, 0)
    )
    Images.screen.blit(shadow_surface, (x + 2, y + 2))
    text_surface = game.font.render(
        f"Score: {score}", True, (255, 255, 255)
    )
    Images.screen.blit(text_surface, (x, y))


def draw_heart(game: GameSystem, x: int, y: int) -> None:
    lives = game.player_creature.player._lives
    heart_alive = Images.player_heart
    heart_dead = Images.pygame_heart_kell
    spacing = 45

    if lives <= 3:
        for i in range(3):
            heart_x = x + i * spacing
            if i < lives:
                Images._drow(heart_alive, (heart_x, y))
            else:
                Images._drow(heart_dead, (heart_x, y))
    else:
        Images._drow(heart_alive, (x, y))
        font = pygame.font.SysFont("Arial", 30, bold=True)
        shadow_surface = font.render(f"x {lives}", True, (0, 0, 0))
        Images.screen.blit(shadow_surface, (x + 47, y + 7))
        text_surface = font.render(f"x {lives}", True, (255, 255, 255))
        Images.screen.blit(text_surface, (x + 45, y + 5))
