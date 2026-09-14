from abc import ABC, abstractmethod


class Creature(ABC):

    def __init__(self, spawn_point: tuple[int, int]):
        self.x: int, self.y: int = spawn_point
    
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


class Player(Creature):

    def __init__(self, spawn_point, lives: int = 3, super_timer: int):
        super().__init__(spawn_point)
        self._lives = lives
        self._score: int = 0
        self._speed: int = 100
        self._is_super = False
        self._super_timer = super_timer

    def move(self) -> None:
        pass

    def draw(self) -> None:
        pass

    def handle_input(keys: list) -> None:
        pass

    def eat(self, item_type: str) -> int:
        pass

    def respawn(self) -> None:
        pass

    def update_speed(self, new_speed: int, time: int) -> None:
        self._speed = new_speed
