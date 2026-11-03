import pygame

from .monster import Monster
from .player import Player
from ..block import Block, Mape
from photos.loderimages import Images
from .algo_monster import AlgoMonster
from .bfs import PathFinder


class BabyZombie(Monster):
    def __init__(
        self, spawn_point: tuple[int, int], is_hardcore: bool = False
    ) -> None:
        """
        Initialize the BabyZombie spawn state, movement fields, and
        sprite.
        Apply the faster speed when hardcore mode is enabled.
        made by: Mohammad Abu Aresh
        """
        super().__init__(spawn_point, is_hardcore)
        self.spawn_point = spawn_point
        self.locaion: tuple[float, float] = (
                float(self.spawn_point[0]),
                float(self.spawn_point[1]),
                )
        self.live: bool = True
        self.next_point: tuple[int, int] | None = None
        if is_hardcore and self.live:
            self.speed = 110
        self.is_hardcore: bool = is_hardcore
        self.load_size()

    def load_size(self) -> None:
        """
        Scale the zombie image to the current maze cell size.
        Store the scaled surface for subsequent drawing.
        made by: Mohammad Abu Aresh
        """
        Images._update_size(
            "zombie",
            (Block.size * 0.6, Block.size * 0.9)
        )
        self.image = Images.zombie_new

    def get_render_rect(self, mape: Mape) -> pygame.Rect:
        """
        Return the zombie image rectangle at its current maze position.
        Preserve the zombie-specific vertical drawing offset.
        made by: Mohammad Abu Aresh
        """
        px = mape.origin_x + (self.x + 0.7) * Block.size
        py = mape.origin_y + (self.y + 0.2) * Block.size
        return self.image.get_rect(topleft=(int(px), int(py)))

    def draw(self, mape: Mape) -> None:
        """
        Draw the zombie at its current maze position.
        Render foreground wall blocks afterward to preserve the 2.5D
        layering.
        made by: Mohammad Abu Aresh
        """
        px = mape.origin_x + (self.x + 0.7) * Block.size
        py = mape.origin_y + (self.y + 0.2) * Block.size
        Images._drow(self.image, location=(px, py))
        self._draw_front_blocks(mape)

    def set_hardcore_mode(self, enabled: bool) -> None:
        """
        Update the inherited hardcore flag and the zombie movement
        speed.
        Change speed only while the zombie is alive.
        made by: Mohammad Abu Aresh
        """
        super().set_hardcore_mode(enabled)
        if self.live:
            self.speed = 110 if enabled else 65

#    def move(
#            self, grid: list[list[bool]] | None = None
#            ) -> None:
#        if grid is None or self.target_point is None:
#            return
#
#        if self.next_point is None:
#            self.next_point = PathFinder.next_step(
#                grid,
#                (round(self.x), round(self.y)),
#                self.target_point
#            )
#        if self.next_point is None:
#            return
#
#        next_x, next_y = self.next_point
#        step = Block.size / 150 * self.speed / 100
#        if next_x != self.x:
#            self.x += max(-step, min(step, next_x - self.x))
#        else:
#            self.y += max(-step, min(step, next_y - self.y))
#        self.locaion = (self.x, self.y)
#        if (self.x, self.y) == self.next_point:
#            self.next_point = None

    def follow(
        self, player: Player,
        grid: list[list[bool]] | None = None
    ) -> None:
        """
        Choose the BabyZombie target according to its life and mode
        state.
        Use its spawn, player cell, scatter corner, or direct chase
        target.
        made by: Mohammad Abu Aresh
        """
        if not self.live:
            self.target_point = self.spawn_point

        elif grid is None:
            self.target_point = (
                round(player.x), round(player.y)
                )

        elif self.mode == "scatter":
            self.target_point = (len(grid[0]) - 2, 1)

        else:
            self.target_point = AlgoMonster.get(1)(player)
