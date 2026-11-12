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
        """
        Initialize Witch potion timing, flee tracking, and base
        monster state.
        Load the Witch sprite using the current maze cell size.
        made by: Mohammad Abu Aresh
        """
        super().__init__(spawn_point, is_hardcore)
        self.potion_cooldown: float = 30.0  # cooldown in seconds
        self.potion_timer: float = 0.0
        self.potions: list[SlowPotion] = []
        # i need to define the potion in a hardcore fun
        self.radius_check: int = 4  # 4-block radius
        self._is_fleeing = False
        self._player_cell: tuple[int, int] | None = None
        self.load_size()

    def load_size(self) -> None:
        """
        Scale the Witch sprite for the current maze cell size.
        Store the scaled image surface for drawing.
        made by: Mohammad Abu Aresh
        """
        Images._update_size(
            "witch",
            (Block.size * 0.6, Block.size * 1.8)
        )
        self.image = Images.witch_new

    def throw_slow_potion(self, player: Player) -> bool:
        """
        Apply a slow potion when a living hardcore Witch is near the
        player.
        Measure distance and request the configured five-second
        effect.
        made by: Mohammad Abu Aresh
        """
        if not self.is_hardcore or not self.live or self.frightened:
            return False

        distance = math.sqrt(
            (self.x - player.x) ** 2 + (self.y - player.y) ** 2
        )
        if distance > self.radius_check:
            return False
        self.potions.append(SlowPotion((self.x, self.y), duration=5))
        return True

    def update_potion(self, player: Player, delta_time: float) -> bool:
        self.potion_timer = max(self.potion_timer - delta_time, 0.0)
        landed = False
        for potion in self.potions:
            potion.move((player.x, player.y), delta_time)
            if potion.arrived:
                potion.apply_effect(player)
                landed = True
        self.potions = [p for p in self.potions if not p.arrived]
        if self.potion_timer == 0.0 and self.throw_slow_potion(player):
            self.potion_timer = self.potion_cooldown
        return landed

    def reset_ai(self) -> None:
        super().reset_ai()
        self.potions.clear()

    def _choose_next_point(
        self,
        grid: list[list[bool]],
        current_cell: tuple[int, int],
        player_cell: tuple[int, int] | None = None,
    ) -> tuple[int, int] | None:
        """
        Choose an escape step when Witch is marked as fleeing.
        Otherwise delegate next-cell selection to the base Monster
        method.
        made by: Mohammad Abu Aresh
        """
        if self._is_fleeing and self._player_cell is not None:
            return PathFinder.next_step_away(
                grid, current_cell, self._player_cell
            )
        return super()._choose_next_point(
            grid, current_cell, player_cell
        )

    def follow(
        self,
        player: Player,
        grid: list[list[bool]] | None = None,
    ) -> None:
        """
        Update Witch proximity state and select its current target.
        Flee nearby players, return to spawn when dead, and use
        normal mode targets otherwise.
        made by: Mohammad Abu Aresh
        """
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
