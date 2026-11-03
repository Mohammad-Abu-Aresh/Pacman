from typing import Any
from mazegenerator import MazeGenerator
from photos.loderimages import Images


class Block:
    size: int = 0

    def __init__(self, wall: int) -> None:
        """
        Decode the wall bitmask into the four directional wall
        flags.
        Reject values that contain bits outside the supported wall
        layout.
        made by: Mohammad Abu Aresh
        update by: Abdalghani Abtah
        """
        self.left: bool = True if wall >= 8 else False
        if self.left:
            wall -= 8
        self.bottom: bool = True if wall >= 4 else False
        if self.bottom:
            wall -= 4
        self.right: bool = True if wall >= 2 else False
        if self.right:
            wall -= 2
        self.top: bool = True if wall >= 1 else False
        if self.top:
            wall -= 1
        if wall > 0:
            raise ValueError("walles have value more than it shuld be")

    @classmethod
    def size_update(
            cls, width: int, height: int, columns: int, rows: int
            ) -> int:
        """
        Calculate a cell size that fits the maze within the display
        area.
        Store the selected size on Block and return it to the
        caller.
        made by: Mohammad Abu Aresh
        """
        cell_width: int = int(((width - (width * 0.28)) // columns))
        cell_height: int = int(((height - (height * 0.1)) // rows))
        cls.size = cell_width if cell_width < cell_height else cell_height
        return cls.size


class Mape:
    def __init__(
            self, maze: MazeGenerator,
            ) -> None:
        """
        Build the map, expanded grid, spawn positions, and display
        offsets.
        Calculate the shared cell size after converting maze blocks.
        made by: Mohammad Abu Aresh
        update by: Abdalghani Abtah
        """
        self.width = Images.width
        self.height = Images.height
        self.mape: list[list[Block]] = self.blocks(maze.maze)
        self.columns = len(self.mape[0]) * 2 + 1
        # columns == x in a nother file's
        self.rows = len(self.mape) * 2 + 1
        Block.size_update(self.width, self.height, self.columns, self.rows)
        self.grid = self.every_cell
        self.spawn_point = {
            "player": self._center_spawn_point(self.grid),
            "zombie":   (1, 1),
            "skeleton": (2 * len(self.mape[0]) - 1, 1),
            "enderman": (1, 2 * len(self.mape) - 1),
            "witch":    (2 * len(self.mape[0]) - 1, 2 * len(self.mape) - 1),
        }
        self.origin_x = (
            Images.width - (self.columns * Block.size * 1.4)
            ) // 2
        self.origin_y = (
            Images.height - (self.rows * Block.size * 1.1)
            ) // 2

    @staticmethod
    def _center_spawn_point(
        grid: list[list[bool]],
    ) -> tuple[int, int]:
        """Find the nearest walkable cell to the expanded grid center.
        Use Manhattan distance and stable tie-breaking for each maze seed.
        Return the selected coordinates in the player's (x, y) order.
        made by: Mohammad Abu Aresh
        """
        if not grid or not grid[0]:
            raise ValueError("Maze grid must not be empty")
        if any(len(row) != len(grid[0]) for row in grid):
            raise ValueError("Maze grid must be rectangular")

        center_x = len(grid[0]) // 2
        center_y = len(grid) // 2
        walkable_cells = [
            (x, y)
            for y, row in enumerate(grid)
            for x, is_wall in enumerate(row)
            if not is_wall
        ]
        if not walkable_cells:
            raise ValueError("Maze grid has no walkable spawn cell")
        return min(
            walkable_cells,
            key=lambda point: (
                abs(point[0] - center_x) + abs(point[1] - center_y),
                abs(point[1] - center_y),
                point[1],
                point[0],
            ),
        )

    def blocks(self, lists: list[list[int]]) -> list[list[Block]]:
        """
        Convert each integer in the generated maze into a Block
        object.
        Return the converted maze while preserving its row and
        column order.
        made by: Mohammad Abu Aresh
        update by: Abdalghani Abtah
        """
        res: list[list[Block]] = []
        for lis in lists:
            arr: list[Block] = []
            for i in lis:
                arr.append(Block(i))
            res.append(arr)
        return res

    @property
    def every_cell(self) -> list[list[bool]]:
        """
        Expand maze blocks into a cell grid used for movement and
        pathfinding.
        Mark walls as True and traversable cells as False.
        made by: Abdalghani Abtah
        update by: Mohammad Abu Aresh
        """
        mape2 = self.mape
        x = 2 * len(mape2) + 1
        y = 2 * len(mape2[0]) + 1
        lis: list[list[bool]] = []
        for _ in range(x):
            row: Any = []
            for _ in range(y):
                row.append(True)
            lis.append(row)

        for row in range(len(mape2)):
            for column in range(len(mape2[row])):
                call = mape2[row][column]
                x = 2 * row + 1
                y = 2 * column + 1
                lis[x][y] = False
                if not call.top:
                    lis[x - 1][y] = False
                if not call.bottom:
                    lis[x + 1][y] = False
                if not call.left:
                    lis[x][y - 1] = False
                if not call.right:
                    lis[x][y + 1] = False
        return lis

    @property
    def coordination_42(self) -> list[list[bool]]:
        """
        Build the expanded grid used to place the project
        collectibles.
        Mark cell centers and passages according to each block wall
        layout.
        made by: Abdalghani Abtah
        update by: Mohammad Abu Aresh
        """
        mape2 = self.mape
        x = 2 * len(mape2) + 1
        y = 2 * len(mape2[0]) + 1
        lis: list[list[bool]] = []
        for _ in range(x):
            row: Any = []
            for _ in range(y):
                row.append(True)
            lis.append(row)

        for row in range(len(mape2)):
            for column in range(len(mape2[row])):
                call = mape2[row][column]
                x = 2 * row + 1
                y = 2 * column + 1
                if call.top and call.bottom and call.left and call.right:
                    lis[x][y] = True
                else:
                    lis[x][y] = False
                if not call.top:
                    lis[x - 1][y] = False
                if not call.bottom:
                    lis[x + 1][y] = False
                if not call.left:
                    lis[x][y - 1] = False
                if not call.right:
                    lis[x][y + 1] = False
        return lis
