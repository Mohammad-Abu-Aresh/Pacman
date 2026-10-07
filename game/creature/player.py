# import time
from enum import Enum
from .creature import Creature
from ..block import Mape, Block
from photos.loderimages import Images
import pygame



class Direction(Enum):
    """
    if x 1, meen he going the positave x so he is going like this ->
    if x -1, meen he going the nigative x so he is going like this <-
    same for y
    the tuple is (x, y)
    the y start from 0 and if we get down we have to incres y...
    """
    right = (1, 0)
    left = (-1, 0)
    up = (0, -1)
    down = (0, 1)


class movement:
    move = None
    @classmethod
    def traffic_update(cls, new_move: Direction) -> None:
        cls.move = new_move


class Player(Creature):

    def __init__(
            self, maze_map: Mape,
            lives: int, super_timer: int,
            is_hardcore: bool,
            spawn_point
            ) -> None:
        self.maze = maze_map
        self._lives = lives
        self._super_timer = super_timer

        self.spawn_point: tuple[int, int] = spawn_point

        self.locaion: tuple[float, float] = (
            float(self.spawn_point[0]),
            float(self.spawn_point[1]),
            )
        self.direction: tuple[int, int] = Direction.right
        # we can make it empty temp

        self.x: float = self.locaion[0]
        self.y: float = self.locaion[1]
        # must be update when i move

        self._score: int = 0
        self._speed: int = Block.size / 700

        self._is_super = False

        self.load_size()
        # if is_hardcore:
        #     ...

    def load_size(self) -> None:
        Images._update_size(
            "player",
            size=(Block.size * 0.7, Block.size * 2.8) # 2.8 just on this photo so its temp it was 1.8
        )
        self.image = Images.player_new

    def move(self) -> None:
        self.velx = 0
        self.vely = 0
        if movement.move == Direction.right:
            self.velx = self._speed
        elif movement.move == Direction.left:
            self.velx = -self._speed
        elif movement.move == Direction.up:
            self.vely = -self._speed
        elif movement.move == Direction.down:
            self.vely = self._speed
        self.x += self.velx
        self.y += self.vely

        
        self.rect = pygame.Rect(
            int(self.x),
            int(self.y),
            self.image.get_width(),
            self.image.get_height()
        )



    def die(self) -> None:
        self.telport((800, 800))
        # time.sleep(3) # timer . tic + 3000
        self.respawn

    def handle_input(self, keys: list[bool]) -> None:
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction = Direction.right
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction = Direction.left
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            self.direction = Direction.up
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction = Direction.down

    def eat(self, item_type: str) -> int:
        return 0
        pass

    def respawn(self) -> None:
        self.telport(self.spawn_point)
        self._lives -= 1

    def telport(self, point: tuple[int, int]) -> None:
        self.locaion = (float(point[0]), float(point[1]))
        self.x = self.locaion[0]
        self.y = self.locaion[1]
        self.rect = pygame.Rect(
            int(self.x),
            int(self.y),
            self.image.get_width(),
            self.image.get_height()

        )
    def update_speed(self, new_speed: int, time: int) -> None:
        self._speed = new_speed
