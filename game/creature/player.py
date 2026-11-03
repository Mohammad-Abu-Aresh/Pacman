# import time
from .creature import Creature
from ..block import Mape, Block
from photos.loderimages import Images
import pygame


class Direction():
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
    none = (0, 0)


class movement:
    move: tuple[int, int] = (0, 0)
    new_dir: tuple[int, int] | None = None

    @classmethod
    def traffic_update(
        cls, new_move: tuple[int, int]
    ) -> None:
        """
        Store the currently active player movement direction.
        The Player movement method reads this shared direction each
        frame.
        made by: Abdalghani Abtah
        update by: Mohammad Abu Aresh
        """
        cls.move = new_move

    @classmethod
    def musle_memory(
        cls, new_move: tuple[int, int] | None
    ) -> None:
        """
        Store or clear the next requested player direction.
        The player applies this buffered direction when the next
        cell is legal.
        made by: Abdalghani Abtah
        update by: Mohammad Abu Aresh
        """
        cls.new_dir = new_move


class Player(Creature):
    def __init__(
            self, maze_map: Mape,
            lives: int, super_timer: int,
            is_hardcore: bool,
            spawn_point: tuple[int, int]
            ) -> None:
        """
        Initialize player maze, lives, timers, spawn, position, and
        direction.
        Prepare the score, movement speed, and scaled player image.
        made by: Mohammad Abu Aresh
        update by: Abdalghani Abtah
        """
        self.maze = maze_map
        self.is_hardcore = is_hardcore
        self.myx_lives = lives
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

        self.score: int = 0
        self.base_speed: float = Block.size / 550
        self.speed: float = self.base_speed
        self._slow_timer: float = 0.0
        self._is_super = False
        self.load_size()
        # if is_hardcore:
        #     ...

    def load_size(self) -> None:
        """
        Scale the player sprite using the current maze cell size.
        Store the scaled surface used by the player drawing routine.
        made by: Mohammad Abu Aresh
        """
        Images._update_size(
            "player",
            size=(Block.size * 0.7, Block.size * 2.8)
            # 2.8 just on this photo so its temp it was 1.8
        )
        self.image = Images.player_new
        self.base_speed = Block.size / 550
        if self._slow_timer <= 0:
            self.speed = self.base_speed

    def change_diric(self) -> None:
        """
        Apply a buffered direction when its destination cell is
        walkable.
        Align the player to the relevant grid axis before changing
        direction.
        made by: Abdalghani Abtah
        update by: Mohammad Abu Aresh
        """
        if movement.new_dir is None:
            return

        cell_x = round(self.x) + movement.new_dir[0]
        cell_y = round(self.y) + movement.new_dir[1]

        if self.can_move_to(cell_x, cell_y):
            if movement.new_dir[0] != 0:
                self.y = round(self.y)
            else:
                self.x = round(self.x)

            self.locaion = (self.x, self.y)
            self.direction = movement.new_dir
            movement.traffic_update(movement.new_dir)
            movement.musle_memory(None)
            return
        return

    def can_move_to(self, cell_x: int, cell_y: int) -> bool:
        """
        Check whether a grid coordinate is inside the maze and not a
        wall.
        Return False for coordinates outside the available grid.
        made by: Abdalghani Abtah
        """
        grid = self.maze.every_cell
        if not (0 <= cell_y < len(grid)):
            return False
        if not (0 <= cell_x < len(grid[cell_y])):
            return False
        return not grid[cell_y][cell_x]

    def move(self) -> None:
        """
        Move the player using the shared active direction and
        current speed.
        Stop movement when the next rounded cell is blocked.
        made by: Mohammad Abu Aresh
        update by: Abdalghani Abtah
        """
        dx, dy = movement.move
        if movement.move == Direction.none:
            return
        next_x = self.x + dx * self.speed
        next_y = self.y + dy * self.speed
        if not self.can_move_to(round(next_x), round(next_y)):
            movement.traffic_update(Direction.none)
            return
        self.x = next_x
        self.y = next_y
        self.locaion = (self.x, self.y)

    def die(self) -> None:
        """
        Move the player to the temporary off-maze death coordinates.
        The current method references respawn without invoking it.
        made by: Mohammad Abu Aresh
        """
        self.telport((800, 800))
        # time.sleep(3) # timer . tic + 3000
        self.respawn

    def handle_input(self, keys: list[bool]) -> None:
        """
        Update the player facing direction from the supplied key
        states.
        Support arrow keys and WASD movement keys.
        made by: Mohammad Abu Aresh
        update by: Abdalghani Abtah
        """
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction = Direction.right
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction = Direction.left
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            self.direction = Direction.up
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction = Direction.down

    def eat(self, points: int) -> int:
        """
        Add collected points to the player score.
        Return the updated score after the addition.
        made by: Mohammad Abu Aresh
        update by: Abdalghani Abtah
        """
        self.score += points
        return self.score

    def respawn(self) -> None:
        """
        Return the player to its configured spawn point.
        Decrease the remaining life count after teleporting.
        made by: Mohammad Abu Aresh
        """
        self.telport(self.spawn_point)
        self._lives -= 1
        self._slow_timer = 0.0
        self.speed = self.base_speed

    def telport(self, point: tuple[int, int]) -> None:
        """
        Set the player position to the supplied grid coordinates.
        Refresh the stored location and rebuild the pygame
        rectangle.
        made by: Mohammad Abu Aresh
        update by: Abdalghani Abtah
        """
        self.locaion = (float(point[0]), float(point[1]))
        self.x = self.locaion[0]
        self.y = self.locaion[1]
        self.rect = pygame.Rect(
            int(self.x),
            int(self.y),
            self.image.get_width(),
            self.image.get_height()
        )

    def update_speed(self, new_speed: int, time: float) -> None:
        """
        Store the requested percentage of normal movement speed.
        Keep the slowdown active for the configured duration.
        made by: Mohammad Abu Aresh
        """
        self.speed = self.base_speed * (new_speed / 100.0)
        self._slow_timer = max(self._slow_timer, time)

    def update_effects(self, delta_time: float) -> None:
        """Advance temporary player effects and restore normal speed on expiry.
        Keep the slowdown active for its configured duration.
        made by: Mohammad Abu aresh
        """
        if self._slow_timer <= 0:
            return
        self._slow_timer = max(
            0.0, self._slow_timer - max(delta_time, 0.0)
        )
        if self._slow_timer == 0:
            self.speed = self.base_speed
