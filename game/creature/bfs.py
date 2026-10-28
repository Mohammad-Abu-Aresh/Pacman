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
        queue: deque[tuple[int, int]] = deque([start])

        came_from: dict[
            tuple[int, int],
            tuple[int, int] | None
        ] = {start: None}

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

    @staticmethod
    def next_step_towards(
        grid: list[list[bool]],
        start: tuple[int, int],
        target: tuple[int, int],
        direction: tuple[int, int] = (0, 0),
        reverse: bool = False,
    ) -> Optional[tuple[int, int]]:
        options = PathFinder._ordered_neighbors(grid, start)
        if not options:
            return None

        reverse_step = (start[0] - direction[0], start[1] - direction[1])
        if reverse and direction != (0, 0) and reverse_step in options:
            return reverse_step
        if start == target and not reverse:
            return None

        if direction != (0, 0):
            forward_options = [
                cell for cell in options if cell != reverse_step
            ]
            if forward_options:
                options = forward_options

        return min(
            options,
            key=lambda cell: (
                (cell[0] - target[0]) ** 2
                + (cell[1] - target[1]) ** 2
            ),
        )

    @staticmethod
    def next_step_away(
        grid: list[list[bool]],
        start: tuple[int, int],
        from_cell: tuple[int, int],
    ) -> Optional[tuple[int, int]]:
        options = PathFinder._ordered_neighbors(grid, start)
        if not options:
            return None

        best_step: Optional[tuple[int, int]] = None
        best_score: tuple[float, int] | None = None
        for candidate in options:
            path = PathFinder.find_path(grid, candidate, from_cell)
            maze_distance = float(len(path)) if path else float("inf")
            straight_distance = (
                (candidate[0] - from_cell[0]) ** 2
                + (candidate[1] - from_cell[1]) ** 2
            )
            score = (maze_distance, straight_distance)
            if best_score is None or score > best_score:
                best_step = candidate
                best_score = score
        return best_step

    # ==================== internals ====================

    @staticmethod
    def _neighbors(
            grid: list[list[bool]], cell: tuple[int, int]
            ) -> list[tuple[int, int]]:
        """Open cells adjacent to `cell` (walls and out-of-bounds dropped)."""
        x, y = cell
        result = []
        for direction in (
                Direction.up, Direction.down,
                Direction.left, Direction.right
                ):
            nxt = (x + direction[0], y + direction[1])
            if PathFinder._walkable(grid, nxt):
                result.append(nxt)
        return result

    @staticmethod
    def _ordered_neighbors(
        grid: list[list[bool]],
        cell: tuple[int, int],
    ) -> list[tuple[int, int]]:
        x, y = cell
        result = []
        for dx, dy in ((0, -1), (-1, 0), (0, 1), (1, 0)):
            candidate = (x + dx, y + dy)
            if PathFinder._walkable(grid, candidate):
                result.append(candidate)
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
        path: list[tuple[int, int]] = []
        node: Optional[tuple[int, int]] = goal
        while node is not None:
            path.append(node)
            node = came_from[node]
        path.reverse()
        return path
