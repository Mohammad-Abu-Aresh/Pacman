import random
import pygame

from .abilities import EnderPearl
from .monster import Monster
from .player import Direction, Player
from ..block import Mape, Block
from photos import Images
from .algo_monster import AlgoMonster


class Enderman(Monster):
    SAFE_DISTANCE: int = 4

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
        self.teleport_cooldown: float = 10.0  # every 20 seconds
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

    def throw_pearl_and_teleport(
        self, grid: list[list[bool]], player: Player
    ) -> bool:
        """
        Create an EnderPearl destination and move a living hardcore
        Enderman.
        Choose random coordinates within the supplied maze bounds.
        made by: Mohammad Abu Aresh
        """
        if not self.is_hardcore or not self.live or self.frightened:
            return False

        destination = self._pick_destination(grid, player)
        if destination is None:
            return False

        self.current_pearl = EnderPearl(destination, (self.x, self.y))
        return True

    def _pick_destination(
        self, grid: list[list[bool]], player: Player
    ) -> tuple[int, int] | None:
        here = (round(self.x), round(self.y))
        open_cells = [
            (x, y)
            for y, row in enumerate(grid)
            for x, is_wall in enumerate(row)
            if not is_wall and (x, y) != here
        ]
        far_cells = [
            cell for cell in open_cells
            if abs(cell[0] - round(player.x))
            + abs(cell[1] - round(player.y)) >= self.SAFE_DISTANCE
        ]
        choices = far_cells or open_cells
        return random.choice(choices) if choices else None

    def update_teleport(
        self, player: Player, grid: list[list[bool]], delta_time: float
    ) -> list[tuple[float, float]]:
        bursts: list[tuple[float, float]] = []
        self.teleport_timer = max(self.teleport_timer - delta_time, 0.0)
        pearl = self.current_pearl
        if pearl is not None:
            pearl.move(delta_time)
            if pearl.arrived:
                self.current_pearl = None
                if self.live:
                    self._land(pearl)
                    bursts.append((self.x, self.y))
        elif self.teleport_timer == 0.0:
            origin = (self.x, self.y)
            if self.throw_pearl_and_teleport(grid, player):
                self.teleport_timer = self.teleport_cooldown
                bursts.append(origin)
        return bursts

    def _land(self, pearl: EnderPearl) -> None:
        self.x = float(pearl.target_x)
        self.y = float(pearl.target_y)
        self.locaion = (self.x, self.y)
        self.next_point = None
        self.movement_direction = Direction.none
        self.reverse_pending = False

    def reset_ai(self) -> None:
        super().reset_ai()
        self.current_pearl = None
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
