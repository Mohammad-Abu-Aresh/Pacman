from abc import ABC, abstractmethod


class Creature(ABC):

    def __init__(self, spawn_point: tuple[int, int]):
<<<<<<< HEAD
        self.x: int
        self.y: int
        self.x, self.y = spawn_point
=======
        self.x: int = spawn_point[0]
        self.y: int = spawn_point[1]
>>>>>>> mabu
    
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

<<<<<<< HEAD
    def __init__(self, spawn_point, super_timer: int, lives: int = 3):
=======
    def __init__(self, spawn_point, lives: int = 3, super_timer: int = 15):
>>>>>>> mabu
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
