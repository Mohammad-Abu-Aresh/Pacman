from collections import deque
from typing import Optional
from .player import Direction


class PathFinder:
    """Shared BFS pathfinding over the expanded maze grid.

    The grid comes from Mape.every_cell and is indexed grid[y][x]:
    True = wall, False = open corridor. Movement is 4-directional,
    one cell at a time.

    Used by the MonsterController right after an AlgoMonster strategy
    returns a target cell — strategies choose "where", this chooses "how".

    find_path() returns the full cell list (start -> goal), next_step()
    returns only the first move, which is what a monster needs per tick.
    """

    # ==================== public API ====================

    @staticmethod
    def find_path(
            grid: list[list[bool]], start: tuple[int, int],
            goal: tuple[int, int]
            ) -> Optional[list[tuple[int, int]]]:
        """Shortest path start -> goal as a list of cells, or None."""
        if start == goal:
            return [start]
        if not PathFinder._walkable(grid, goal):
            return None
        queue: deque = deque([start])
        came_from: dict = {start: None}
        while queue:
            current = queue.popleft()
            if current == goal:
                return PathFinder._reconstruct(came_from, goal)
            for nxt in PathFinder._neighbors(grid, current):
                if nxt not in came_from:
                    came_from[nxt] = current
                    queue.append(nxt)
        return None

    @staticmethod
    def next_step(
            grid: list[list[bool]], start: tuple[int, int],
            goal: tuple[int, int]
            ) -> Optional[tuple[int, int]]:
        """The first cell on the shortest path, or None if stuck."""
        path = PathFinder.find_path(grid, start, goal)
        if path is None or len(path) < 2:
            return None
        return path[1]

    # ==================== internals ====================

    @staticmethod
    def _neighbors(
            grid: list[list[bool]], cell: tuple[int, int]
            ) -> list[tuple[int, int]]:
        """Open cells adjacent to `cell` (walls and out-of-bounds dropped)."""
        x, y = cell
        result = []
        for direction in (
                Direction.UP, Direction.DOWN,
                Direction.LEFT, Direction.RIGHT
                ):
            nxt = (x + direction[0], y + direction[1])
            if PathFinder._walkable(grid, nxt):
                result.append(nxt)
        return result

    @staticmethod
    def _walkable(grid: list[list[bool]], cell: tuple[int, int]) -> bool:
        x, y = cell
        if y < 0 or y >= len(grid) or x < 0 or x >= len(grid[0]):
            return False
        return not grid[y][x]

    @staticmethod
    def _reconstruct(
            came_from: dict, goal: tuple[int, int]
            ) -> list[tuple[int, int]]:
        path = []
        node: Optional[tuple[int, int]] = goal
        while node is not None:
            path.append(node)
            node = came_from[node]
        path.reverse()
        return path
