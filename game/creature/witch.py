import math
from .monster import Monster
from .abilities import SlowPotion
from .player import Player
from ..block import Block
from photos import Images
from .algo_monster import AlgoMonster
from .bfs import PathFinder


class Witch(Monster):
    def __init__(
        self, spawn_point: tuple[int, int], is_hardcore: bool = False
    ) -> None:
        super().__init__(spawn_point, is_hardcore)
        self.potion_cooldown: float = 30.0  # cooldown in seconds
        # i need to define the potion in a hardcore fun
        self.radius_check: int = 4  # 4-block radius
        self._is_fleeing = False
        self._player_cell: tuple[int, int] | None = None
        self.load_size()

    def load_size(self) -> None:
        Images._update_size(
            "witch",
            (Block.size * 0.6, Block.size * 1.8)
        )
        self.image = Images.witch_new

    def throw_slow_potion(self, player: Player) -> None:
        """
        throws a slow potion if player is within radius
        witch is alive, and in hardcore mode
        """
        if not self.is_hardcore or not self.live:
            return

        distance = math.sqrt(
            (self.x - player.x) ** 2 + (self.y - player.y) ** 2
        )
        if distance <= self.radius_check:
            potion = SlowPotion((self.x, self.y), duration=5)
            potion.apply_effect(player)

    def _choose_next_point(
        self,
        grid: list[list[bool]],
        current_cell: tuple[int, int],
    ) -> tuple[int, int] | None:
        if self._is_fleeing and self._player_cell is not None:
            return PathFinder.next_step_away(
                grid, current_cell, self._player_cell
            )
        return super()._choose_next_point(grid, current_cell)

    def follow(
        self,
        player: Player,
        grid: list[list[bool]] | None = None,
    ) -> None:
        distance = math.sqrt(
            (self.x - player.x) ** 2 + (self.y - player.y) ** 2
        )
        self._player_cell = (round(player.x), round(player.y))
        self._is_fleeing = self.live and (
            distance <= AlgoMonster.SHY_RADIUS * AlgoMonster.GRID_SCALE
        )

        if not self.live:
            self.target_point = self.spawn_point
        elif grid is None:
            self.target_point = (
                round(player.x),
                round(player.y),
            )
        elif self._is_fleeing:
            self.target_point = (round(self.x), round(self.y))
        elif self.mode == "scatter":
            self.target_point = (1, len(grid) - 2)
        else:
            self.target_point = AlgoMonster.get(4)(
                self, player, grid, None
            )
