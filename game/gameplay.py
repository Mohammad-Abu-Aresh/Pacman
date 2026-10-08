from time import time

import pygame
import random

from game.creature.player import Direction, movement
from .creature import Diamond, Netherite
from photos.loderimages import Images
from typing import Dict, Any
from .creature import Control_creature
from mazegenerator import MazeGenerator
from .block import Mape, Block
from .game_modes import Mod


class GameSystem:
    backphoto: dict[int, Any] = {
        1: Images.level_1,
        2: Images.level_2,
        }

    def __init__(self, config: Dict[str, Any], hardcore_mode: bool = False, cheating: bool = False) -> None:
        self.num = 0
        self.config = config
        self.current_level: int = 1
        self.max_levels: int = config["max_levels"]
        self.lives: int = self.config.get("lives", 3)
        self.level_max_time: int = self.config.get("level_max_time", 90)
        self.hardcore_mode = hardcore_mode
        self.cheating = cheating
        self.row = 7
        self.column = 7
        self.load_level()
        self.time_left: float = float(self.level_max_time)
        pygame.font.init()
        self.font = pygame.font.SysFont(None, 36)
        self.player_creature = Control_creature(
            maze_map=self.maze_map,
            lives=3,
            super_timer=15
            )
        self.mobs: tuple[object] = (
                self.player_creature.player,
                self.player_creature.BabyZombie,
                self.player_creature.Skeleton,
                self.player_creature.Enderman,
                self.player_creature.witch,
                )

    def load_level(self) -> None:
        
        if self.current_level == 1:
            self.num += 1
            self.seed = self.config.get("seed", 42)
            self.row = 11
            self.column = 7
            self.backimage = self.backphoto[self.current_level + 1]
            self.background = pygame.transform.scale(
                self.backimage,
                (
                    Images.width,
                    Images.height,
                ),
            )
        else:
            self.num += 1
            self.seed = random.randint(1, 2004)
            if self.num == 3 or self.num == 6 or self.num == 9 or self.num == 12:
                self.row += 2
                self.column += 1
            else:
                self.mobs[0]._super_timer -= 2
        maze = MazeGenerator(size=(self.row, self.column), seed=self.seed)
        self.maze_map = Mape(maze)
        Images._update_size("wall", size=(Block.size * 2.1, Block.size * 1.85))
        self.time_left = self.level_max_time

        self.collectibles: list[Diamond | Netherite] = []
        height = len(self.maze_map.every_cell)
        max_y = height - 1
        max_x = len(self.maze_map.every_cell[0]) - 1 if height > 0 else 0
        corners = {
            (1, 1),
            (max_x - 1, 1),
            (1, max_y - 1),
            (max_x - 1, max_y - 1)
            }
        for y, row in enumerate(self.maze_map.coordination_42):
            for x, cell in enumerate(row):
                if not cell:
                    if (x, y) in corners:
                        self.collectibles.append(Netherite(Images.screen, self.config, x, y))
                    else:

                        self.collectibles.append(Diamond(Images.screen, self.config, x, y))


    def next_level(self) -> None:
        if self.current_level <= self.max_levels:
            self.current_level += 1
        else:
            self.current_level = 1
        if self.current_level > self.config["max_levels"]:
            Mod.updatemod(Mod.MAIN_MENU_SCREEN)
        self.load_level()
        movement.traffic_update(None)
        self.player_creature.refresh(self.maze_map)

    def update(self, time: float, cheating: bool = False) -> None:
        if self.time_left > 0:
            self.time_left -= time
        else:
            Mod.updatemod(Mod.GAME_OVER_SCREEN)
        keys = pygame.key.get_pressed()
        self.player_creature.player.move()
        if keys[pygame.K_n] and cheating:
            self.next_level()

    def draw(self) -> None:

        _ = self._draw_maze(
            self.maze_map.origin_x,
            self.maze_map.origin_y
            )


        for item in self.collectibles:
            item.draw(self.maze_map)

        for mob in self.mobs:
            mob.draw(self.maze_map)

        self._draw_timer()

    def _draw_maze(
            self,
            origin_x: int,
            origin_y: int
            ) -> list[list[tuple[tuple[int, int], bool]]]:
        maze_bool = self.maze_map.every_cell

        row = self.maze_map.columns
        cell_size = Block.size
        for item in self.collectibles:
            item.draw(self.maze_map)

        Images.screen.blit(self.background, (0, 0))
        lis = []
        for y, row in enumerate(maze_bool):
            ls = []
            for x, cell in enumerate(row):
                location_x = origin_x + (x * cell_size)
                location_y = origin_y + (y * cell_size)
                ls.append(((location_x, location_y), cell))
                if cell:
                    Images._drow(
                        Images.wall_new,
                        location=(location_x, location_y)
                        )
                else:
                    continue
            lis.append(ls)

        return lis

    def _draw_timer(self) -> None:
        text_surface = self.font.render(
                f"{int(self.time_left)}", True, (255, 255, 255)
                )
        Images.screen.blit(text_surface, (20, 20))


