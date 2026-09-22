import pygame
import random
from typing import Dict, Any
from mazegenerator import MazeGenerator
from .block import Mape, Block
from .game_modes import Mod


class GameSystem:
    backphoto: dict[int, any] = {
        1:pygame.image.load("photos/background/background1.jpg")
        }
    def __init__(self, screen: pygame.Surface, config: Dict[str, Any]) -> None:

        self.screen = screen
        self.config = config
        self.current_level: int = 1
        self.max_levels: int = config["max_levels"]
        self.score: int = 0
        self.lives: int = self.config.get("lives", 3)
        self.level_max_time: int = self.config.get("level_max_time", 90)
        self.row = 7
        self.column = 7
        self.time_left: float = float(self.level_max_time)
        self.load_level()
        pygame.font.init()
        self.font = pygame.font.SysFont(None, 36)

    def load_level(self) -> None:

        if self.current_level == 1:
            self.seed = self.config.get("seed", 42)
            self.row = 11
            self.column = 5
            self.backimage = self.backphoto[self.current_level]
            self.background = pygame.transform.scale(
                    self.backimage,
                      (
                          self.screen.get_width(),
                          self.screen.get_height()
                          )
                )
        else:
            self.seed = random.randint(1, 2004)
            self.row += 2
            self.column += 1
            # self.background = background(self.current_level)
        maze = MazeGenerator(size=(self.row, self.column), seed=self.seed)
        self.maze_map = Mape(
            maze, self.screen.get_width(), self.screen.get_height()
            )
        self.time_left = self.level_max_time

    def next_level(self) -> None:
        if self.current_level <= self.max_levels:
            self.current_level += 1
        else:
            self.current_level = 1
        if self.current_level > self.config["max_levels"]:
            Mod.updatemod(Mod.MAIN_MENU_SCREEN)
        self.load_level()

    def update(self, time: float) -> None:
        if self.time_left > 0:
            self.time_left -= time
        else:
            Mod.updatemod(Mod.MAIN_MENU_SCREEN)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_s]:
            self.next_level()

    def draw(self) -> None:
        _ = self._draw_maze()
        self._draw_timer()

    def _draw_maze(self) -> list[list[tuple[tuple[int, int], bool]]]:
        maze_bool = self.maze_map.every_cell

        row = self.maze_map.columns
        columns = self.maze_map.rows
        cell_size = Block.size
        view_maze = row * cell_size
        length_maze = columns * cell_size

        width = self.screen.get_width()
        height = self.screen.get_height()

        self.screen.blit(self.background, (0, 0))

        starting_point_x = (width - view_maze) // 2 - 10
        starting_point_y = (height - length_maze * 1.05) // 2 
        lis = []
        for y, row in enumerate(maze_bool):
            ls = []
            for x, cell in enumerate(row):
                location_x = starting_point_x + (x * cell_size)
                location_y = starting_point_y + (y * cell_size)
                ls.append(((location_x, location_y), cell))
                rect = pygame.Rect(
                    location_x, location_y, cell_size, cell_size
                )
                if cell:
                    pygame.draw.rect(self.screen, (30, 50, 160), rect)
                else:
                    continue
            lis.append(ls)

        return lis

    def _draw_timer(self) -> None:
        text_surface = self.font.render(
                f"{int(self.time_left)}", True, (255, 255, 255)
                )
        self.screen.blit(text_surface, (20, 20))

    def _draw_entities(self) -> None:
        pass
