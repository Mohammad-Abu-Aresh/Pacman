from abc import ABC, abstractmethod


class Entity(ABC):

    def __init__(self, first_coordinates: tuple[int, int]):
        self.x = first_coordinates[0]
        self.y = first_coordinates[1]
    
    @abstractmethod
    def move() -> None:
        pass

    @abstractmethod
    def draw() -> None:
        pass

    def check_wall_collision() -> None:
        pass


class Player(Entity):

    def __init__(self, first_coordinates, lives, super_timer):
        super().__init__(first_coordinates)
        self.lives = lives
        self.score = 0
        self.is_super = False
        self.super_timer = super_timer

    def move() -> None:
        pass

    def draw() -> None:
        pass

    def handle_input(keys: list) -> None:
        pass

    def eat_item(item_type: str) -> int:
        pass

    def respawn() -> None:
        pass