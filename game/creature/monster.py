
from abc import ABC, abstractmethod

from ..block import Block
from .bfs import PathFinder
from .creature import Creature
from .player import Player


class Monster(Creature, ABC):
    def __init__(
        self, spawn_point: tuple[int, int],
        is_hardcore: bool = False
    ) -> None:
        self.spawn_point: tuple[int, int] = spawn_point
        self.x = float(spawn_point[0])
        self.y = float(spawn_point[1])
        self.locaion: tuple[float, float] = (self.x, self.y)
        self.target_point: tuple[int, int] | None = None
        self.next_point: tuple[int, int] | None = None
        self.live: bool = True
        self.speed: int = 65
        self.is_following: bool = True
        self.is_hardcore: bool = is_hardcore

    @abstractmethod
    def follow(self, player: Player) -> None:
        pass

    def move(
        self, grid: list[list[bool]] | None = None
    ) -> None:
        if grid is None or self.target_point is None:
            return

        if self.next_point is None:
            self.next_point = PathFinder.next_step(
                grid,
                (round(self.x), round(self.y)),
                self.target_point,
            )

        if self.next_point is None:
            return

        next_x, next_y = self.next_point
        step = Block.size / 150 * self.speed / 100

        if next_x != round(self.x):
            self.y = float(round(self.y))
            self.x += max(-step, min(step, next_x - self.x))
        else:
            self.x = float(round(self.x))
            self.y += max(-step, min(step, next_y - self.y))

        self.locaion = (self.x, self.y)

        if self.x == next_x and self.y == next_y:
            self.next_point = None

    def set_hardcore_mode(self, enabled: bool) -> None:
        self.is_hardcore = enabled

    def die(self) -> None:
        """
        sets the monster to dead state and
        resets its target to spawn point
        """
        self.live = False
        self.is_following = False
        self.target_point = self.spawn_point
        self.next_point = None
