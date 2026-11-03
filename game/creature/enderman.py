import random
import pygame

from .abilities import EnderPearl
from .monster import Monster
from .player import Player
from ..block import Mape, Block
from photos import Images
from .algo_monster import AlgoMonster


class Enderman(Monster):

    def __init__(
        self, spawn_point: tuple[int, int], is_hardcore: bool = False
    ) -> None:
        """
        Initialize Enderman teleport state, chaser reference, and
        base monster data.
        Load the image at the current maze cell size.
        made by: Mohammad Abu Aresh
        """
        super().__init__(spawn_point, is_hardcore)
        self.teleport_cooldown: float = 20.0  # every 20 seconds
        self.current_pearl: EnderPearl | None = None
        self.chaser: Monster | None = None
        self.load_size()

    def load_size(self) -> None:
        """
        Scale the Enderman image for the current maze cell size.
        Store the scaled image surface for drawing.
        made by: Mohammad Abu Aresh
        """
        Images._update_size(
            "enderman",
            (Block.size * 0.6, Block.size * 2.8)
        )
        self.image = Images.enderman_new

    def get_render_rect(self, mape: Mape) -> pygame.Rect:
        """
        Return the Enderman image rectangle at its current maze position.
        Preserve the Enderman-specific vertical drawing offset.
        made by: Mohammad Abu Aresh
        """
        px = mape.origin_x + (self.x + 0.7) * Block.size
        py = mape.origin_y + (self.y - 1) * Block.size
        return self.image.get_rect(topleft=(int(px), int(py)))

    def draw(self, mape: Mape) -> None:
        """
        Draw Enderman at its adjusted maze position.
        Render foreground blocks afterward to preserve the 2.5D
        layering.
        made by: Mohammad Abu Aresh
        """
        px = mape.origin_x + (self.x + 0.7) * Block.size
        py = mape.origin_y + (self.y - 1) * Block.size
        Images._drow(self.image, location=(px, py))
        self._draw_front_blocks(mape)

    def throw_pearl_and_teleport(self, maze_bounds: tuple[int, int]) -> None:
        """
        Create an EnderPearl destination and move a living hardcore
        Enderman.
        Choose random coordinates within the supplied maze bounds.
        made by: Mohammad Abu Aresh
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
        """
        Select Enderman target using its life state and current
        ghost mode.
        Use the spawn, player, scatter corner, or vector strategy
        with its chaser.
        made by: Mohammad Abu Aresh
        """
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
