from .abilities import EnderPearl
from .monster import Monster
from .player import Player
from ..block import Mape, Block
from photos import Images
import random
from .algo_monster import AlgoMonster


class Enderman(Monster):

    def __init__(
        self, spawn_point: tuple[int, int], is_hardcore: bool = False
    ) -> None:
        super().__init__(spawn_point, is_hardcore)
        self.teleport_cooldown: float = 20.0  # every 20 seconds
        self.current_pearl: EnderPearl | None = None
        self.chaser: Monster | None = None
        self.load_size()

    def load_size(self) -> None:
        Images._update_size(
            "enderman",
            (Block.size * 0.6, Block.size * 2.8)
        )
        self.image = Images.enderman_new

    def draw(self, mape: Mape) -> None:
        px = mape.origin_x + (self.x + 0.7) * Block.size
        py = mape.origin_y + (self.y - 1) * Block.size
        Images._drow(self.image, location=(px, py))
        self._draw_front_blocks(mape)

    def throw_pearl_and_teleport(self, maze_bounds: tuple[int, int]) -> None:
        """
        teleports the enderman using an enderpearl
        if alive and in hardcore mode
        """
        if not self.is_hardcore or not self.live:
            return

        rand_x = random.randint(0, maze_bounds[0])
        rand_y = random.randint(0, maze_bounds[1])

        self.current_pearl = EnderPearl((rand_x, rand_y))
        self.x = rand_x
        self.y = rand_y

    def follow(
        self,
        player: Player,
        grid: list[list[bool]] | None = None,
        chaser: Monster | None = None,
    ) -> None:
        if not self.live:
            self.target_point = self.spawn_point
        elif grid is None:
            self.target_point = (
                round(player.x),
                round(player.y),
            )
        elif self.mode == "scatter":
            self.target_point = (len(grid[0]) - 2, len(grid) - 2)
        else:
            chaser = chaser or self.chaser
            self.target_point = AlgoMonster.get(3)(
                self, player, grid, chaser
            )
