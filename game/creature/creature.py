from abc import ABC, abstractmethod
from ..block import Mape, Block
from photos.loderimages import Images

class Creature(ABC):
    @abstractmethod
    def __init__(self) -> None:
        ...

    @abstractmethod
    def move(self) -> None:
        pass

    def draw(self, mape: Mape) -> None:
        px = mape.origin_x + (self.x + 0.7) * Block.size
        py = mape.origin_y + (self.y - 0.5) * Block.size
        Images._drow(self.image, location=(px, py))

    @abstractmethod
    def die(self) -> None:
        self.image._drow(self.locaion)

    # def check_wall_collision() -> None:
    #    pass


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
        self.mobs: tuple[object] = (
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


        # def update_spown_point(obj: str) -> None:

