from math import sqrt
from typing import Callable, Optional
from .creature import Creature
from .player import Player
from .bfs import PathFinder


# signature shared by every strategy:
# (monster, player, grid, chaser) -> target cell (x, y)
Strategy = Callable[
        [Creature, Player, list[list[bool]], Optional[Creature]],
        tuple[int, int]
        ]


class AlgoMonster:
    """Pre-BFS target selection.

    Each strategy answers one question: "where is this monster trying to
    go right now?" The controller feeds the returned cell into the shared
    BFS pathfinder — strategies never touch pathfinding or movement.

    Grid coordinates follow Mape.every_cell: True = wall, False = corridor,
    indexed as grid[row][col] i.e. grid[y][x].

    Monster roles (matching the Minecraft cast):
        1. BabyZombie — the Chaser:  goes directly at the player's
                                     current cell, always.
        2. Skeleton   — from ahead:  aims several cells in front of the
                                     player, cutting him off at corners.
        3. Enderman   — from the side: mirrors the chaser through a pivot
                                     ahead of the player, closing in from
                                     the flank — needs `chaser`.
        4. Witch      — the shy one: chases from afar, but loses her nerve
                                     and retreats to her corner once the
                                     player gets close.
    """

    AHEAD_TILES = 4     # Skeleton: how far ahead of the player to aim
    VECTOR_TILES = 2    # Enderman: pivot distance ahead of the player
    SHY_RADIUS = 8      # Witch: chase beyond this distance, flee inside it

    # ==================== strategies ====================

    @staticmethod
    def target_player(
            monster: Creature, player: Player, grid: list[list[bool]],
            chaser: Optional[Creature] = None
            ) -> tuple[int, int]:
        """BabyZombie — straight at the player's current cell."""
        return (PathFinder.find_path(player.x, player.y))

    @staticmethod
    def target_ahead(
            monster: Creature, player: Player, grid: list[list[bool]],
            chaser: Optional[Creature] = None
            ) -> tuple[int, int]:
        """Skeleton — AHEAD_TILES cells in front of the player."""
        dx, dy = player.direction
        target = (
                player.x + dx * AlgoMonster.AHEAD_TILES,
                player.y + dy * AlgoMonster.AHEAD_TILES
                )
        return AlgoMonster._clamp(target, grid)

    @staticmethod
    def target_vector(
            monster: Creature, player: Player, grid: list[list[bool]],
            chaser: Optional[Creature] = None
            ) -> tuple[int, int]:
        """Enderman — mirror the chaser through a pivot ahead of the player.

        Falls back to chasing the player directly if no chaser is given.
        """
        if chaser is None:
            return AlgoMonster.target_player(monster, player, grid)
        dx, dy = player.direction
        pivot = (
                player.x + dx * AlgoMonster.VECTOR_TILES,
                player.y + dy * AlgoMonster.VECTOR_TILES
                )
        target = (
                pivot[0] + (pivot[0] - chaser.x),
                pivot[1] + (pivot[1] - chaser.y)
                )
        return AlgoMonster._clamp(target, grid)

    @staticmethod
    def target_shy(
            monster: Creature, player: Player, grid: list[list[bool]],
            chaser: Optional[Creature] = None
            ) -> tuple[int, int]:
        """Witch — chases from afar, but retreats to her corner up close."""
        distance = sqrt((monster.x - player.x) ** 2
                        + (monster.y - player.y) ** 2)
        if distance > AlgoMonster.SHY_RADIUS:
            return (player.x, player.y)
        return (0, len(grid) - 1)  # bottom-left scatter corner

    # ==================== registry ====================

    STRATEGIES: dict[int, Strategy] = {
            1: target_player,   # BabyZombie — direct chaser
            2: target_ahead,    # Skeleton   — comes from ahead
            3: target_vector,   # Enderman   — comes from the side
            4: target_shy,      # Witch      — the shy one
            }

    @classmethod
    def get(cls, strategy_id: int) -> Strategy:
        """Fetch a strategy by its monster ID."""
        return cls.STRATEGIES[strategy_id]

    # ==================== helpers ====================

    @staticmethod
    def _clamp(
            target: tuple[int, int], grid: list[list[bool]]
            ) -> tuple[int, int]:
        """Keep a target inside the maze so BFS never goes out of bounds."""
        x, y = target
        return (
                min(max(x, 0), len(grid[0]) - 1),
                min(max(y, 0), len(grid) - 1)
                )
