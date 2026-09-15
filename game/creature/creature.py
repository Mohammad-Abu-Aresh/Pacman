from abc import ABC, abstractmethod


class Creature(ABC):

    def __init__(self, spawn_point: tuple[int, int]) -> None:
        self.x: int = spawn_point[0]
        self.y: int = spawn_point[1]
        self.direction: int = 0  # 1: Up, 2: Right, 4: Down, 8: Left

    @abstractmethod
    def move(self) -> None:
        pass

    @abstractmethod
    def draw(self) -> None:
        pass

    @abstractmethod
    def die(self) -> None:
        pass


class Player(Creature):

    def __init__(
            self, spawn_point: tuple[int, int],
            super_timer: int = 0, lives: int = 3
            ) -> None:
        super().__init__(spawn_point)
        self._lives: int = lives
        self._score: int = 0
        self._speed: int = 100
        self._is_super: bool = False
        self._super_timer: int = super_timer
        self._can_teleport: bool = False

    def move(self) -> None:
        pass

    def draw(self) -> None:
        pass

    def die(self) -> None:
        pass

    def handle_input(self, keys: list) -> None:
        pass

    def eat(self, item_type: str) -> int:
        return 0

    def respawn(self) -> None:
        pass

    def update_speed(self, new_speed: int) -> None:
        self._speed = new_speed
