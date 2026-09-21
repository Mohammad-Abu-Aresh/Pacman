import pygame
import random
from typing import Dict, Any
from mazegenerator import MazeGenerator  # type: ignore[import-untyped]
from .block import Mape
from . import game_modes


class GameSystem:
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
        self.font = pygame.font.SysFont("font/minecraft.ttf", 36)

    def load_level(self) -> None:

        if self.current_level == 1:
            self.seed = self.config.get("seed", 42)
            self.row = 7
            self.column = 7
        else:
            self.seed = random.randint(1, 2004)
            self.row += 1
            self.column += 1
        maze = MazeGenerator(size=(self.row, self.column), seed=self.seed)
        self.maze_map = Mape(maze)
        self.time_left = self.level_max_time

    def next_level(self) -> None:
        if self.current_level <= self.max_levels:
            self.current_level += 1
        else:
            self.current_level = 1
        if self.current_level > self.config["max_levels"]:
            game_modes.state_variable = game_modes.MAIN_MENU_SCREEN
        self.load_level()

    def update(self, time: float) -> None:
        if self.time_left > 0:
            self.time_left -= time
        else:
            game_modes.state_variable = game_modes.MAIN_MENU_SCREEN
        keys = pygame.key.get_pressed()
        if keys[pygame.K_s]:
            self.next_level()

    def draw(self) -> None:
        _ = self._draw_maze()
        self._draw_timer()

    def _draw_maze(self) -> list[list[tuple[tuple[int, int], bool]]]:
        maze_bool = self.maze_map.every_cell
        width = self.screen.get_width()
        height = self.screen.get_height()
        columns = len(maze_bool[0])
        rows = len(maze_bool)
        cell_size = (width // columns + height // rows) // 3
        view_maze = columns * cell_size
        length_maze = rows * cell_size
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

    def _draw_timer(self) -> None:
        text_surface = self.font.render(
                f"{int(self.time_left)}", True, (255, 255, 255)
                )
        self.screen.blit(text_surface, (20, 20))

    def _draw_entities(self) -> None:
        pass
