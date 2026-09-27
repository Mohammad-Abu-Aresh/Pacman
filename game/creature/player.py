import time
from .creature import Creature
from ..block import Mape, Block
import pygame


class Player(Creature):

    def __init__(
            self, maze_map: Mape,
            lives: int, super_timer: int,
            is_hardcore: bool,
            ) -> None:
        self.maze = maze_map
        self._image = pygame.image.load("photos/player/steve.png")
        self.spown_point: tuple[int, int] = (
            maze_map.width // 2,
            maze_map.height // 2,
        )
        self.size: int = Block.size * 2
        self.locaion: tuple[float, float] = (
            float(self.spown_point[0]),
            float(self.spown_point[1]),
            )
        self.x: float = self.locaion[0]
        self.y: float = self.locaion[1]
        self._lives = lives
        self._score: int = 0
        self._speed: int = 100 * Block.size
        self._is_super = False
        self._super_timer = super_timer

    def move(self) -> None:
        pass

    def die(self) -> None:
        self.telport((800, 800))
        time.sleep(3)
        self.respawn

    def draw(self) -> None:
        pass

    def handle_input(self, keys: list[str]) -> None:
        pass

    def eat(self, item_type: str) -> int:
        return 0
        pass

    def respawn(self) -> None:
        self.telport(self.spown_point)
        self._lives -= 1

    def telport(self, point: tuple[int, int]) -> None:
        ...

    def update_speed(self, new_speed: int, time: int) -> None:
        self._speed = new_speed
