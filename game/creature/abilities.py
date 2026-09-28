from .player import Player
from abc import ABC, abstractmethod
import pygame


# ===============================================
# hardcore objects (only used in hardcore mode)
# ===============================================

class Abilities(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def move(self) -> None:
        pass

    @abstractmethod
    def draw(self, image: pygame.Surface) -> None:
        pass


class Arrow(Abilities):

    def __init__(
        self, spawn_point: tuple[int, int],
        direction: int, speed: int = 300
    ) -> None:
        self.x: int = spawn_point[0]
        self.y: int = spawn_point[1]
        self.direction: int = direction
        self.speed: int = speed  # 300% of player speed

    def move(self) -> None:
        pass


class EnderPearl(Abilities):

    def __init__(self, target_point: tuple[int, int]) -> None:
        self.target_x: int = target_point[0]
        self.target_y: int = target_point[1]


class SlowPotion(Abilities):

    def __init__(self, position: tuple[int, int], duration: int = 5) -> None:
        self.x: int = position[0]
        self.y: int = position[1]
        self.duration: int = duration  # slowdown duration in seconds

    def apply_effect(self, player: Player) -> None:
        player.update_speed(35, self.duration)  # slow down the player
