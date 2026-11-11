from abc import ABC, abstractmethod
from ..block import Mape, Block
from photos.loderimages import Images
from .ghost_modes import set_group_level
from .ghost_state import (
    activate_group_frightened,
    check_ghost_collisions,
    reset_group_frightened,
    update_group_frightened,
)
import pygame


class Creature(ABC):
    @abstractmethod
    def __init__(
        self,
        image: pygame.Surface,
        spawn_point: tuple[int, int],
    ) -> None:
        """
        Initialize the shared spawn point, position, and image
        fields.
        Concrete creature classes supply their own movement and
        sizing methods.
        made by: Mohammad Abu Aresh
        update by: Abdalghani Abtah
        """
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
        """
        Declare the movement interface required by concrete
        creatures.
        Each creature implementation defines how its position is
        updated.
        made by: Mohammad Abu Aresh
        """
        pass

    @abstractmethod
    def load_size(self) -> None:
        """
        Declare the sprite-sizing hook required by concrete
        creatures.
        Subclasses load or scale the image used by their drawing
        method.
        made by: Mohammad Abu Aresh
        """
        ...

    def get_render_rect(self, mape: Mape) -> pygame.Rect:
        """
        Return the creature image rectangle at its current maze position.
        Preserve the shared creature drawing offset.
        made by: Mohammad Abu Aresh
        """
        px = mape.origin_x + (self.x + 0.7) * Block.size
        py = mape.origin_y + (self.y - 0.5) * Block.size
        return self.image.get_rect(topleft=(int(px), int(py)))

    def draw(self, mape: Mape) -> None:
        """
        Draw the creature using the maze origin and shared cell
        size.
        Draw foreground wall blocks afterward to maintain the 2.5D
        effect.
        made by: Mohammad Abu Aresh
        """
        px = mape.origin_x + (self.x + 0.7) * Block.size
        py = mape.origin_y + (self.y - 0.5) * Block.size
        Images._drow(self.image, location=(px, py))
        self._draw_front_blocks(mape)

    def _draw_front_blocks(self, mape: Mape) -> None:
        """
        Draw bottom-facing wall sections that visually overlap the
        creature.
        Use the creature grid position to select the nearby
        foreground blocks.
        made by: Mohammad Abu Aresh
        """
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
        """
        Declare the death-handling hook for concrete creature
        classes.
        Subclasses provide the state changes required when a
        creature dies.
        made by: Mohammad Abu Aresh
        update by: Abdalghani Abtah
        """
        Images._drow(self.image, self.locaion)
        ...


class Control_creature:
    def __init__(
            self,
            maze_map: Mape,
            lives: int = 3,
            super_timer: int = 15,
            is_hardcore: bool = False,
                 ) -> None:
        """
        Create the player and four monster instances for the current
        maze.
        Connect the Enderman chaser reference and collect the shared
        creature tuple.
        made by: Mohammad Abu Aresh
        update by: Abdalghani Abtah
        """
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

        self.witch = Witch(maze_map.spawn_point["witch"], is_hardcore)
        self.Skeleton = Skeleton(
            maze_map.spawn_point["skeleton"], is_hardcore
        )
        self.BabyZombie = BabyZombie(
            maze_map.spawn_point["zombie"], is_hardcore
        )
        self.Enderman = Enderman(
            maze_map.spawn_point["enderman"], is_hardcore
        )
        self.Enderman.chaser = self.BabyZombie
        self.mobs: tuple[Creature, ...] = (
            self.player,
            self.witch,
            self.Skeleton,
            self.BabyZombie,
            self.Enderman,
        )
        self.frightened_timer = 0.0
        self.frightened_cycle = 0

    def activate_frightened(self, duration: float) -> None:
        """
        Delegate group frightened activation to the ghost state
        helpers.
        The helper updates the group timer, player indicator, and
        each monster.
        made by: Mohammad Abu Aresh
        """
        activate_group_frightened(self, duration)

    def update_frightened(self, delta_time: float) -> None:
        """
        Update the shared frightened timer using the elapsed frame
        time.
        The delegated helper also synchronizes the player super-
        state indicator.
        made by: Mohammad Abu Aresh
        """
        update_group_frightened(self, delta_time)

    def refresh(self, mape: Mape, level: int = 1) -> None:
        """
        Attach the creature group to a newly generated maze.
        Refresh spawn points, positions, sprite sizes, AI states,
        and frightened state.
        made by: Mohammad Abu Aresh
        """
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
        set_group_level(self, level)
        reset_group_frightened(self)

        # def update_spown_point(obj: str) -> None:

    def update_abilities(self, delta_time: float) -> bool:
        self.player.update_slow(delta_time)
        self.witch.update_potion(self.player, delta_time)
        return self.Skeleton.update_arrows(
            self.player, self.maze_mape, delta_time
        )

    def check_collision(self, points_per_ghost: int = 200) -> bool:
        """
        Delegate monster collision checks and frightened-ghost
        scoring.
        Return whether a dangerous monster hit the player.
        made by: Mohammad Abu Aresh
        """
        return check_ghost_collisions(self, points_per_ghost)

    def reset_mobs(self) -> None:
        """
        Stop buffered player movement and reset group frightened
        state.
        Move each monster to its spawn point and restore its AI
        state.
        made by: Mohammad Abu Aresh
        """
        from .player import Direction, movement

        movement.traffic_update(Direction.none)
        movement.musle_memory(None)
        self.player.direction = Direction.none

        reset_group_frightened(self)
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
