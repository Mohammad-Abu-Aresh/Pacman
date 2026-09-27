from abc import ABC, abstractmethod
from ..block import Mape,Block


class Creature(ABC):
    @abstractmethod
    def __init__(self, maze_map: Mape) -> None:
        ...

    @abstractmethod
    def move(self) -> None:
        pass

    @abstractmethod
    def draw(self) -> None:
        pass

    @abstractmethod
    def die(self) -> None:
        ...

    # def check_wall_collision() -> None:
    #    pass

class Control_creature:
    def __init__(self,
            maze_map: Mape,
            lives: int = 3,
            super_timer: int = 15,
            is_hardcore: bool = False
                 ) -> None:
        from .player import Player
        from .monster import (
                Skeleton, Enderman, BabyZombie, Witch
            )
        self.Player = Player(
            maze_map,
            lives,
            super_timer,
            is_hardcore,
            )
        self.Skeleton = Skeleton()
        self.BabyZombie = BabyZombie()
        self.Enderman = Enderman()
        