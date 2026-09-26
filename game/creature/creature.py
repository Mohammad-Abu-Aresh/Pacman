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