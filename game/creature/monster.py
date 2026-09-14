from creature import Creature
from abc import ABC, abstractmethod


class Monster(Creature):
    def __init__(self, spawn_point: tuple[int, int]) -> None:
        super().__init__(spawn_point)
        self.live: bool = True
        self.speed = 65 # player speed - %35
        self.is_folowing: bool = True

    @abstractmethod
    def follow(self) -> None:
        ...

    @abstractmethod
    def hardcore_mode(self) -> None:
        ...

class Bybe_zombie(Monster):
    def __init__(self, spawn_point: tuple[int, int], ) -> None:
        super().__init__(spawn_point)

    def hardcore_mode(self) -> None:
        self.speed = 110
