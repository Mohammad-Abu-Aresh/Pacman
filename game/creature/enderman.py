import random
import pygame

from .projectiles import EnderPearl
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
        self.teleport_cooldown: float = 15.0  # every 15 seconds
        self.teleport_timer: float = self.teleport_cooldown
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

    def move(
        self,
        grid: list[list[bool]] | None = None,
        delta_time: float = 1 / 60,
        player_cell: tuple[int, int] | None = None,
    ) -> None:
        """Pause Enderman movement while its pearl animation is active.
        Resume normal path movement after the teleport is complete.
        made by: Mohammad Abu aresh
        """
        if self.current_pearl is not None:
            return
        super().move(grid, delta_time, player_cell)

    def throw_pearl_and_teleport(
        self, grid: list[list[bool]], player: Player
    ) -> None:
        """
        Create an EnderPearl destination and move a living hardcore
        Enderman.
        Choose random coordinates within the supplied maze bounds.
        made by: Mohammad Abu Aresh
        """
        if not self.hardcore_active or self.current_pearl is not None:
            return

        walkable = [
            (x, y)
            for y, row in enumerate(grid)
            for x, is_wall in enumerate(row)
            if not is_wall
            and (x, y) != (round(self.x), round(self.y))
        ]
        safer_cells = [
            cell for cell in walkable
            if (cell[0] - player.x) ** 2 + (cell[1] - player.y) ** 2 >= 9
        ]
        destinations = safer_cells or walkable
        if not destinations:
            return
        target = random.choice(destinations)
        self.current_pearl = EnderPearl(
            target, spawn_point=(self.x, self.y)
        )

    def update_hardcore_ability(
        self,
        delta_time: float,
        player: Player,
        grid: list[list[bool]],
    ) -> None:
        """Advance the Ender Pearl and teleport after its visual arrives.
        Freeze the cooldown and projectile while the Enderman is frightened.
        made by: Mohammad Abu aresh
        """
        if not self.is_hardcore or not self.live:
            self.current_pearl = None
            return
        if self.frightened:
            self.current_pearl = None
            return
        if self.current_pearl is not None:
            arrived = not self.current_pearl.update(delta_time)
            if arrived:
                self.x = float(self.current_pearl.target_x)
                self.y = float(self.current_pearl.target_y)
                self.locaion = (self.x, self.y)
                self.next_point = None
                self.target_point = None
                self.current_pearl = None
            return
        self.teleport_timer = max(
            0.0, self.teleport_timer - max(delta_time, 0.0)
        )
        if self.teleport_timer <= 0:
            self.throw_pearl_and_teleport(grid, player)
            self.teleport_timer = self.teleport_cooldown

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
