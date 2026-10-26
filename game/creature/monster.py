
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

    @staticmethod
    def _step_towards(
        current: float,
        target: float,
        distance: float,
    ) -> float:
        remaining = target - current
        if abs(remaining) <= distance:
            return target
        return current + (
            distance if remaining > 0 else -distance
        )

    def move(
        self,
        grid: list[list[bool]] | None = None,
        delta_time: float = 1 / 60,
    ) -> None:
        if grid is None or self.target_point is None:
            return

        delta_time = min(max(delta_time, 0.0), 0.05)
        current_cell = (round(self.x), round(self.y))

        if self.next_point is not None:
            next_x, next_y = self.next_point

            distance = (
                abs(next_x - current_cell[0])
                + abs(next_y - current_cell[1])
            )

            in_bounds = (
                0 <= next_y < len(grid)
                and 0 <= next_x < len(grid[next_y])
            )

            if (
                distance > 1
                or not in_bounds
                or grid[next_y][next_x]
            ):
                self.next_point = None

        if self.next_point is None:
            self.next_point = PathFinder.next_step(
                grid,
                current_cell,
                self.target_point,
            )

        if self.next_point is None:
            return

        next_x, next_y = self.next_point
        step = 5.0 * (self.speed / 100.0) * delta_time

        if next_y == self.y:
            self.x = self._step_towards(
                self.x, next_x, step
            )
        else:
            self.y = self._step_towards(
                self.y, next_y, step
            )

        self.locaion = (self.x, self.y)
        if (self.x, self.y) == self.next_point:
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
