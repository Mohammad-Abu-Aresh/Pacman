import pygame
from .monster import Monster
from ..block import Block
from .player import Player
from .projectiles import Arrow
from ..block import Mape
from .algo_monster import AlgoMonster


_SKELETON_FRONT = pygame.image.load(
    "photos/monsters/skeleton/front skeleton.png"
)
_SKELETON_SIDE = pygame.image.load(
    "photos/monsters/skeleton/Side_skeleton.png"
)
_SKELETON_BACK = pygame.image.load(
    "photos/monsters/skeleton/back skeleton.png"
)


class Skeleton(Monster):

    def __init__(
        self, spawn_point: tuple[int, int], is_hardcore: bool = False
    ) -> None:
        """
        Initialize the Skeleton shooting state and base monster
        attributes.
        Prepare its sprite, direction field, and active arrow
        collection.
        made by: Mohammad Abu Aresh
        """
        super().__init__(spawn_point, is_hardcore)
        self.shoot_cooldown: float = 3.0  # cooldown between shots in seconds
        self.shoot_timer: float = self.shoot_cooldown
        self.active_arrows: list[Arrow] = []  # if len(arr) > 0 dont shot again
        self.direction: int = 0
        self.load_size()
        self.next_point: tuple[int, int] | None = None

        # tempr = 0 becose ge is not folowing a target yet

    def load_size(self) -> None:
        """
        Scale the Skeleton sprite for the current maze cell size.
        Store the scaled image surface for drawing.
        made by: Mohammad Abu Aresh
        """
        size = (
            max(int(Block.size * 0.6), 1),
            max(int(Block.size * 1.8), 1),
        )
        self.front_image = pygame.transform.scale(_SKELETON_FRONT, size)
        self.side_image = pygame.transform.scale(_SKELETON_SIDE, size)
        self.back_image = pygame.transform.scale(_SKELETON_BACK, size)
        self.image = self.front_image

    def move(
        self,
        grid: list[list[bool]] | None = None,
        delta_time: float = 1 / 60,
        player_cell: tuple[int, int] | None = None,
    ) -> None:
        super().move(grid, delta_time, player_cell)
        self._update_facing_image()

    def _update_facing_image(self) -> None:
        """Select the Skeleton sprite matching its current movement direction.
        Keep the frightened blue sprite until the fear timer expires.
        made by: Mohammad Abu aresh
        """
        if self.frightened or not self.live:
            return
        dx, dy = self.movement_direction
        if dy < 0:
            self.image = self.back_image
        elif dy > 0 or dx == 0:
            self.image = self.front_image
        else:
            self.image = self.side_image
            if dx < 0:
                self.image = pygame.transform.flip(
                    self.image, True, False
                )

    def has_line_of_sight(
        self, player: Player, mape: Mape
    ) -> bool:
        """
        Check whether the living Skeleton and player share a clear
        row or column.
        Return False when an intervening wall blocks the straight
        path.
        made by: Mohammad Abu Aresh
        """
        if not self.live:
            return False

        grid = mape.every_cell

        # Same column check
        if round(self.x) == round(player.x):
            min_y, max_y = min(self.y, player.y), max(self.y, player.y)
            for y in range(round(min_y) + 1, round(max_y)):
                if grid[y][round(self.x)]:  # true if there is a wall
                    return False
            return True

        # Same row check
        if round(self.y) == round(player.y):
            min_x, max_x = min(self.x, player.x), max(self.x, player.x)
            for x in range(round(min_x) + 1, round(max_x)):
                if grid[round(self.y)][x]:  # true if there is a wall
                    return False
            return True

        return False

    def shoot_arrow(
        self, player: Player, mape: Mape
    ) -> None:
        """
        Create an Arrow when hardcore mode, life state, and sight
        checks allow it.
        Do not create another arrow while one is already active.
        made by: Mohammad Abu Aresh
        """
        if not self.hardcore_active:
            return

        if len(self.active_arrows) > 0:
            return

        if self.has_line_of_sight(player, mape):
            direction = (player.x - self.x, player.y - self.y)
            arrow = Arrow((self.x, self.y), direction)
            self.active_arrows.append(arrow)

    def update_hardcore_ability(
        self, delta_time: float, player: Player, mape: Mape
    ) -> bool:
        """Update the Skeleton firing cooldown and active arrows.
        Pause firing and arrow movement while the Skeleton is frightened.
        made by: Mohammad Abu aresh
        """
        if not self.is_hardcore or not self.live:
            self.active_arrows.clear()
            return False
        if self.frightened:
            self.active_arrows.clear()
            return False
        self.shoot_timer = max(
            0.0, self.shoot_timer - max(delta_time, 0.0)
        )
        if self.shoot_timer <= 0 and not self.active_arrows:
            self.shoot_arrow(player, mape)
            if self.active_arrows:
                self.shoot_timer = self.shoot_cooldown
        for arrow in self.active_arrows[:]:
            arrow.update(delta_time, mape.every_cell)
            if arrow.hits_player(player):
                self.active_arrows.remove(arrow)
                return True
            if not arrow.active:
                self.active_arrows.remove(arrow)
        return False

#    def move(self, grid: list[list[bool]] | None = None) -> None:
#        if grid is None or self.target_point is None:
#            return
#
#        if self.next_point is None:
#            self.next_point = PathFinder.next_step(
#                grid,
#                (round(self.x), round(self.y)),
#                self.target_point
#            )
#        if self.next_point is None:
#            return
#
#        next_x, next_y = self.next_point
#        step = Block.size / 150 * self.speed / 100
#
#        if next_x != self.x:
#            self.y = float(round(self.y))
#            self.x += max(-step, min(step, next_x - self.x))
#        else:
#            self.x = float(round(self.x))
#            self.y += max(-step, min(step, next_y - self.y))
#
#        self.locaion = (self.x, self.y)
#        if (self.x, self.y) == self.next_point:
#            self.next_point = None

    def follow(
        self, player: Player,
        grid: list[list[bool]] | None = None
    ) -> None:
        """
        Choose the Skeleton target from its life state and current
        ghost mode.
        Use its spawn, player cell, scatter corner, or ahead-target
        strategy.
        made by: Mohammad Abu Aresh
        """
        if not self.live:
            self.target_point = self.spawn_point
        elif grid is None:
            self.target_point = (
                round(player.x), round(player.y)
            )
        elif self.mode == "scatter":
            self.target_point = (1, 1)
        else:
            self.target_point = AlgoMonster.get(2)(
                self, player, grid, None
            )
