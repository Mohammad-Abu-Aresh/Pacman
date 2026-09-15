import pygame
import random
from typing import Dict, Any
from mazegenerator import MazeGenerator  # type: ignore[import-untyped]
from .block import Mape


class GameSystem:
    def __init__(self, screen: pygame.Surface, config: Dict[str, Any]) -> None:
        self.screen = screen
        self.config = config
        self.current_level: int = 1
        self.max_levels: int = 10
        self.score: int = 0
        self.lives: int = self.config.get("lives", 3)
        self.level_max_time: int = self.config.get("level_max_time", 90)
        self.time_left: float = float(self.level_max_time)
        self.load_level()

    def load_level(self) -> None:
        if self.current_level == 1:
            self.seed = self.config.get("seed", 42)
        else:
            self.seed = random.randint(1, 2004)

        maze = MazeGenerator(seed=self.seed)
        self.maze_map = Mape(maze)

        self.time_left = self.level_max_time

    def update(self) -> None:
        pass

    def draw(self) -> None:
        _ = self._draw_maze()

    def _draw_maze(self) -> list[list[tuple[tuple[int, int], bool]]]:
        maze_bool = self.maze_map.every_cell
        cell_size = 25
        view_maze = len(maze_bool[0]) * cell_size
        length_maze = len(maze_bool) * cell_size
        starting_point_x = (self.screen.get_width() - view_maze) // 2
        starting_point_y = (self.screen.get_height() - length_maze) // 2
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
                    pygame.draw.rect(self.screen, (0, 0, 0), rect)
            lis.append(ls)

        return lis

    def _draw_entities(self) -> None:
        pass
