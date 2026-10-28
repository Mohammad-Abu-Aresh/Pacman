from abc import ABC, abstractmethod
from ..block import Mape, Block
from photos.loderimages import Images
import pygame


class Creature(ABC):
    @abstractmethod
    def __init__(
        self,
        image: pygame.Surface,
        spawn_point: tuple[int, int],
    ) -> None:
        self.spawn_point = spawn_point
        self.locaion: tuple[float, float] = (
            float(spawn_point[0]),
            float(spawn_point[1]),
        )
        self.x: float = self.locaion[0]
        self.y: float = self.locaion[1]
        self.image = image

    @abstractmethod
    def move(self) -> None:
        pass

    @abstractmethod
    def load_size(self) -> None:
        ...

    def draw(self, mape: Mape) -> None:
        px = mape.origin_x + (self.x + 0.7) * Block.size
        py = mape.origin_y + (self.y - 0.5) * Block.size
        Images._drow(self.image, location=(px, py))
        self._draw_front_blocks(mape)

    def _draw_front_blocks(self, mape: Mape) -> None:
        cell_x = round(self.x)
        cell_y = round(self.y)
        row = cell_y // 2

        if not 0 <= row < len(mape.mape):
            return

        if cell_x % 2 == 0:
            columns: tuple[int, int] = (cell_x // 2 - 1, cell_x // 2)
        else:
            columns = (cell_x // 2, 0)

        for column in columns:
            if not 0 <= column < len(mape.mape[row]):
                continue
            if not mape.mape[row][column].bottom:
                continue

            wall_x = column * 2 + 1
            wall_y = (row + 1) * 2
            Images._drow(
                Images.wall_new,
                location=(
                    mape.origin_x + wall_x * Block.size,
                    mape.origin_y + wall_y * Block.size,
                ),
            )

    @abstractmethod
    def die(self) -> None:
        self.image._drow(self.locaion)
        ...


class Control_creature:
    def __init__(
            self,
            maze_map: Mape,
            lives: int = 3,
            super_timer: int = 15,
            is_hardcore: bool = False,
                 ) -> None:
        from .player import Player
        # from .algo_monster import AlgoMonster

        # import mobs
        from .skeleton import Skeleton
        from .enderman import Enderman
        from .babyzombie import BabyZombie
        from .witch import Witch
        self.maze_mape = maze_map

        self.player = Player(
            maze_map,
            lives,
            super_timer,
            is_hardcore,
            maze_map.spawn_point["player"]
            )

        self.witch = Witch(maze_map.spawn_point["witch"])
        self.Skeleton = Skeleton(maze_map.spawn_point["skeleton"])
        self.BabyZombie = BabyZombie(maze_map.spawn_point["zombie"])
        self.Enderman = Enderman(maze_map.spawn_point["enderman"])
        self.Enderman.chaser = self.BabyZombie
        self.mobs: tuple[Creature, ...] = (
            self.player,
            self.witch,
            self.Skeleton,
            self.BabyZombie,
            self.Enderman,
        )

    def refresh(self, mape: Mape) -> None:
        self.maze_mape = mape
        self.player.maze = mape
        self.player.spawn_point = mape.spawn_point["player"]
        self.witch.spawn_point = mape.spawn_point["witch"]
        self.Skeleton.spawn_point = mape.spawn_point["skeleton"]
        self.BabyZombie.spawn_point = mape.spawn_point["zombie"]
        self.Enderman.spawn_point = mape.spawn_point["enderman"]
        for mob in self.mobs:
            mob.load_size()
            mob.x, mob.y = mob.spawn_point
            mob.locaion = (float(mob.x), float(mob.y))
        for mob in (
            self.witch, self.Skeleton, self.BabyZombie, self.Enderman
        ):
            mob.reset_ai()

        # def update_spown_point(obj: str) -> None:

    def check_collision(self) -> bool:
        collision_distance_sq: float = 0.4
        for mob in (
            self.BabyZombie,
            self.Skeleton,
            self.Enderman,
            self.witch,
        ):
            if not mob.live:
                continue

            dx = self.player.x - mob.x
            dy = self.player.y - mob.y
            if dx * dx + dy * dy <= collision_distance_sq:
                return True

        return False

    def reset_mobs(self) -> None:
        from .player import Direction, movement

        movement.traffic_update(Direction.none)
        movement.musle_memory(None)
        self.player.direction = Direction.none

        for mob in (
            self.BabyZombie,
            self.Skeleton,
            self.Enderman,
            self.witch
        ):
            mob.x = float(mob.spawn_point[0])
            mob.y = float(mob.spawn_point[1])

            mob.locaion = (mob.x, mob.y)
            mob.reset_ai()
