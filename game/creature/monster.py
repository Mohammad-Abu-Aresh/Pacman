
from abc import ABC, abstractmethod
from .creature import Creature
from .player import Player


class Monster(Creature, ABC):

    def __init__(
        self, spawn_point: tuple[int, int], is_hardcore: bool = False
    ) -> None:
        self.spawn_point: tuple[int, int] = spawn_point
        self.x, self.y = spawn_point
        self.target_point: tuple[int, int] = None
        self.live: bool = True
        self.speed: int = 65  # 65% of player speed
        self.is_following: bool = True
        self.is_hardcore: bool = is_hardcore

    @abstractmethod
    def follow(self, player: Player) -> None:
        pass

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
