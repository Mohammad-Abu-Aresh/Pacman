from typing import Any
from mazegenerator import MazeGenerator
from photos.loderimages import Images


class Block:
    size: int = 0

    def __init__(self, wall: int) -> None:
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
        cell_width: int = int(((width - (width * 0.28)) // columns))
        cell_height: int = int(((height - (height * 0.1)) // rows))
        cls.size = cell_width if cell_width < cell_height else cell_height
        return cls.size


class Mape:
    def __init__(
            self, maze: MazeGenerator,
            ) -> None:
        self.width = Images.width
        self.height = Images.height
        self.mape: list[list[Block]] = self.blocks(maze.maze)
        self.columns = len(self.mape[0]) * 2 + 1
        # columns == x in a nother file's
        self.rows = len(self.mape) * 2 + 1
        Block.size_update(self.width, self.height, self.columns, self.rows)
        self.spawn_point: dict[str, tuple[int, int]] = {
            "zombie": (0, 0),
            "skeleton": (len(self.mape[0], 0)),
            "enderman": (0, len(self.mape)),
            "witch": (len(self.mape[0]), len(self.mape)),
        }

    def blocks(self, lists: list[list[int]]) -> list[list[Block]]:
        res: list[list[Block]] = []
        for lis in lists:
            arr: list[Block] = []
            for i in lis:
                arr.append(Block(i))
            res.append(arr)
        return res

    @property
    def every_cell(self) -> list[list[bool]]:
        mape2 = self.mape
        x = 2 * len(mape2) + 1
        y = 2 * len(mape2[0]) + 1
        lis: list[list[bool]] = []
        for i in range(x):
            row: Any = []
            for j in range(y):
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
