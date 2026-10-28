from .monster import Monster
from ..block import Block
from photos import Images
from .player import Player
from .abilities import Arrow
from ..block import Mape
from .algo_monster import AlgoMonster
from .bfs import PathFinder


class Skeleton(Monster):

    def __init__(
        self, spawn_point: tuple[int, int], is_hardcore: bool = False
    ) -> None:
        super().__init__(spawn_point, is_hardcore)
        self.shoot_cooldown: float = 3.0  # cooldown between shots in seconds
        self.active_arrows: list[Arrow] = []  # if len(arr) > 0 dont shot again
        self.direction: int = 0
        self.load_size()
        self.next_point: tuple[int, int] | None = None

        # tempr = 0 becose ge is not folowing a target yet

    def load_size(self) -> None:
        Images._update_size(
            "skeleton",
            (Block.size * 0.6, Block.size * 1.8)
        )
        self.image = Images.skeleton_new

    def has_line_of_sight(
        self, player: Player, mape: Mape
    ) -> bool:
        """
        Checks if the skeleton and Player are in the same row or column
        with no wall collisions between them
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
        shoots an arrow only if hardcore mode is active
        creature is alive and has line of sight
        """
        if not self.is_hardcore or not self.live:
            return

        if len(self.active_arrows) > 0:
            return

        if self.has_line_of_sight(player, mape):
            arrow = Arrow((self.x, self.y), self.direction)
            self.active_arrows.append(arrow)

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
