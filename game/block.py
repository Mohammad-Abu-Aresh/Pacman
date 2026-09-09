class Block:
    def __init__(self, wall: int, x: int, y: int) -> None:
        self.x: int = x
        self.y: int = y

        self.left: bool = True if wall >= 8 else False
        if self.left:
            wall -= 8

        self.bottom: bool = True if wall >= 4 else False
        if self.bottom:
            wall -= 4

        self.right: bool = True if wall >= 2 else False
        if self.right:
            wall -= 2

        self.right: bool = True if wall >= 1 else False
        if self.right:
            wall -= 1

        if wall > 0:
            print("walles have value more than it shuld be")
            exit(1)
