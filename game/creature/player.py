import time
from .creature import Creature
from ..block import Mape, Block
from photos.loderimages import Images


class Direction:
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


class Player(Creature):

    def __init__(
            self, maze_map: Mape,
            lives: int, super_timer: int,
            is_hardcore: bool,
            ) -> None:
        self.maze = maze_map
        self._lives = lives
        self._super_timer = super_timer

        self._image = Images.player
        self.spown_point: tuple[int, int] = (
            maze_map.width // 2,
            maze_map.height // 2,
        )

        Images._update_size(
            Images.player,
            size=(Block.size * 1.8, Block.size)
            )
        
        self.locaion: tuple[float, float] = (
            float(self.spown_point[0]),
            float(self.spown_point[1]),
            )
        self.direction: tuple[int, int] = Direction.right
        # we can make it empty temp

        self.x: float = self.locaion[0]
        self.y: float = self.locaion[1]
        # must be update when i move 

        self._score: int = 0
        self._speed: int = 100 * Block.size // 33

        self._is_super = False

        if is_hardcore:
            ...

    def move(self) -> None:
        pass

    def die(self) -> None:
        self.telport((800, 800))
        # time.sleep(3) # timer . tic + 3000
        self.respawn

    def draw(self) -> None:
        pass

    # def handle_input(self, keys: list[str]) -> None:
    #     pass

    def eat(self, item_type: str) -> int:
        return 0
        pass

    def respawn(self) -> None:
        self.telport(self.spown_point)
        self._lives -= 1

    def telport(self, point: tuple[int, int]) -> None:
        ...

    def update_speed(self, new_speed: int, time: int) -> None:
        self._speed = new_speed
