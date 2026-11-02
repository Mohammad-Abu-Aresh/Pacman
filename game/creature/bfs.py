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
        """
        Find a shortest four-direction path between two grid cells
        with BFS.
        Return the ordered path or None when the goal cannot be
        reached.
        made by: Mohammad Abu Aresh
        """
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
        """
        Return the first move on the shortest path from start to
        goal.
        Return None when no route exists or the start already equals
        the goal.
        made by: Mohammad Abu Aresh
        """
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
        """
        Choose a legal neighboring cell that moves toward the
        target.
        Avoid reversing the current direction unless a reversal is
        requested.
        made by: Mohammad Abu Aresh
        """
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
        """
        Choose a legal neighboring cell that increases distance from
        a source.
        Rank options by maze distance, then by straight-line
        distance.
        made by: Mohammad Abu Aresh
        """
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
        """
        Return walkable cells adjacent to the supplied cell.
        Use the shared Direction constants and discard walls or out-
        of-bounds cells.
        made by: Mohammad Abu Aresh
        """
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
        """
        Return legal adjacent cells in a stable up-left-down-right
        order.
        Discard any candidate that is a wall or outside the grid.
        made by: Mohammad Abu Aresh
        """
        x, y = cell
        result = []
        for dx, dy in ((0, -1), (-1, 0), (0, 1), (1, 0)):
            candidate = (x + dx, y + dy)
            if PathFinder._walkable(grid, candidate):
                result.append(candidate)
        return result

    @staticmethod
    def _walkable(grid: list[list[bool]], cell: tuple[int, int]) -> bool:
        """
        Check whether a cell is inside the grid and is not a wall.
        Return False for out-of-bounds coordinates.
        made by: Mohammad Abu Aresh
        """
        x, y = cell
        if y < 0 or y >= len(grid) or x < 0 or x >= len(grid[0]):
            return False
        return not grid[y][x]

    @staticmethod
    def _reconstruct(
            came_from: dict, goal: tuple[int, int]
            ) -> list[tuple[int, int]]:
        """
        Rebuild a path by following predecessor entries back to the
        start.
        Reverse the collected cells so the result runs from start to
        goal.
        made by: Mohammad Abu Aresh
        """
        path: list[tuple[int, int]] = []
        node: Optional[tuple[int, int]] = goal
        while node is not None:
            path.append(node)
            node = came_from[node]
        path.reverse()
        return path
