from .monster import Monster
from ..block import Block
from photos import Images
from .player import Direction, Player
from .abilities import Arrow
from ..block import Mape
from .algo_monster import AlgoMonster


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
        self.active_arrows: list[Arrow] = []  # if len(arr) > 0 dont shot again
        self.direction: tuple[int, int] = Direction.none
        self.shoot_timer: float = 0.0
        self.load_size()
        self.next_point: tuple[int, int] | None = None

        # tempr = 0 becose ge is not folowing a target yet

    def load_size(self) -> None:
        """
        Scale the Skeleton sprite for the current maze cell size.
        Store the scaled image surface for drawing.
        made by: Mohammad Abu Aresh
        """
        Images._update_size(
            "skeleton",
            (Block.size * 0.6, Block.size * 1.8)
        )
        self.image = Images.skeleton_new

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
        if not self.is_hardcore or not self.live or self.frightened:
            return

        if len(self.active_arrows) > 0 or self.shoot_timer > 0:
            return

        direction = self._aim(player)
        if direction != Direction.none and self.has_line_of_sight(
            player, mape
        ):
            self.direction = direction
            arrow = Arrow((self.x, self.y), self.direction)
            self.active_arrows.append(arrow)
            self.shoot_timer = self.shoot_cooldown

    def _aim(self, player: Player) -> tuple[int, int]:
        delta_x = round(player.x) - round(self.x)
        delta_y = round(player.y) - round(self.y)
        if delta_y == 0 and delta_x != 0:
            return Direction.right if delta_x > 0 else Direction.left
        if delta_x == 0 and delta_y != 0:
            return Direction.down if delta_y > 0 else Direction.up
        return Direction.none

    def update_arrows(
        self,
        player: Player,
        mape: Mape,
        delta_time: float,
        can_hurt: bool = True,
    ) -> bool:
        self.shoot_timer = max(self.shoot_timer - delta_time, 0.0)
        player_cell = (round(player.x), round(player.y))
        player_hit = False
        for arrow in self.active_arrows:
            arrow.move(mape.every_cell, delta_time)
            if can_hurt and not arrow.hit_player and arrow.hits(
                player_cell
            ):
                arrow.hit_player = True
                player_hit = True
        self.active_arrows = [
            arrow for arrow in self.active_arrows if arrow.active
        ]
        self.shoot_arrow(player, mape)
        return player_hit

    def reset_ai(self) -> None:
        super().reset_ai()
        self.active_arrows.clear()
        self.shoot_timer = 0.0

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
