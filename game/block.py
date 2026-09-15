from typing import Any
from mazegenerator import MazeGenerator  # type: ignore[import-untyped]


class Block:
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


class Mape:
    def __init__(self, maze: Any = MazeGenerator) -> None:
        self.mape: list[list[Block]] = self.blocks(maze.maze)

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
            r: Any = []
            for j in range(y):
                r.append(True)
            lis.append(r)

        for r in range(len(mape2)):
            for c in range(len(mape2[r])):
                call = mape2[r][c]
                x = 2 * r + 1
                y = 2 * c + 1
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
