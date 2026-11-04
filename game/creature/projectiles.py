from __future__ import annotations
import math
import pygame
from ..block import Block, Mape
from .player import Player


_ARROW_IMAGE = pygame.image.load("photos/abilities/arrow.png")
_PEARL_IMAGE = pygame.image.load("photos/abilities/ender_pearl.png")
_POTION_IMAGE = pygame.image.load("photos/abilities/slow_potion.png")


def _is_walkable(grid: list[list[bool]], x: float, y: float) -> bool:
    """Check whether a projectile position is inside a corridor cell.
    Reject coordinates outside the maze and any cell containing a wall.
    made by: Mohammad Abu aresh
    """
    cell_x, cell_y = round(x), round(y)
    return (
        0 <= cell_y < len(grid)
        and 0 <= cell_x < len(grid[cell_y])
        and not grid[cell_y][cell_x]
    )


class Arrow:
    def __init__(
        self,
        spawn_point: tuple[float, float],
        direction: tuple[float, float],
        speed: float = 6.0,
    ) -> None:
        """Create a cardinal arrow with a permanent wall-bounded lifetime.
        Store its lane, movement speed, and horizontal source sprite.
        made by: Mohammad Abu aresh
        """
        self.x, self.y = spawn_point
        if abs(direction[0]) >= abs(direction[1]):
            self.direction = (1 if direction[0] >= 0 else -1, 0)
        else:
            self.direction = (0, 1 if direction[1] >= 0 else -1)
        self.speed = speed
        self.active = True
        self.hit_registered = False
        size = max(int(Block.size * 0.8), 1)
        scaled = pygame.transform.smoothscale(_ARROW_IMAGE, (size, size))
        self.image = pygame.transform.rotate(scaled, -45)

    def update(self, delta_time: float, grid: list[list[bool]]) -> None:
        """Move along a cardinal lane until the arrow reaches a wall.
        Substeps prevent fast frames from skipping wall cells.
        made by: Mohammad Abu aresh
        """
        distance = self.speed * max(delta_time, 0.0)
        steps = max(1, math.ceil(distance / 0.15))
        step_x = self.direction[0] * distance / steps
        step_y = self.direction[1] * distance / steps
        for _ in range(steps):
            next_x = self.x + step_x
            next_y = self.y + step_y
            if not _is_walkable(grid, next_x, next_y):
                self.active = False
                return
            self.x, self.y = next_x, next_y

    def hits_player(self, player: Player) -> bool:
        """Check whether the arrow reaches the player's current grid cell.
        Use a lane-aligned square hitbox for cardinal projectile travel.
        made by: Mohammad Abu aresh
        """
        dx, dy = self.x - player.x, self.y - player.y
        hit = (
            self.active
            and not self.hit_registered
            and abs(dx) <= 0.5
            and abs(dy) <= 0.5
        )
        self.hit_registered = self.hit_registered or hit
        return hit

    def render(self, mape: Mape) -> None:
        """Draw the arrow at a right-angle rotation matching its lane.
        Position the transparent sprite in maze screen coordinates.
        made by: Mohammad Abu aresh
        """
        angles = {
            (1, 0): 0, (0, -1): 90,
            (-1, 0): 180, (0, 1): 270,
        }
        image = pygame.transform.rotate(
            self.image, angles[self.direction]
        )
        center = (
            round(mape.origin_x + self.x * Block.size),
            round(mape.origin_y + self.y * Block.size),
        )
        screen = pygame.display.get_surface()
        if screen is not None:
            screen.blit(image, image.get_rect(center=center))


class EnderPearl:
    def __init__(
        self,
        target_point: tuple[int, int],
        spawn_point: tuple[float, float],
    ) -> None:
        """Create a pearl animation between the Enderman and its destination.
        Retain the destination for the teleport performed on arrival.
        made by: Mohammad Abu aresh
        """
        self.start_x, self.start_y = spawn_point
        self.target_x, self.target_y = target_point
        self.x, self.y = self.start_x, self.start_y
        self.duration = 0.45
        self.elapsed = 0.0
        self.active = True
        size = max(int(Block.size * 0.55), 1)
        self.image = pygame.transform.smoothscale(_PEARL_IMAGE, (size, size))

    def update(self, delta_time: float) -> bool:
        """Move the pearl marker toward the selected safe destination.
        Return False when the animation has reached its destination.
        made by: Mohammad Abu aresh
        """
        if not self.active:
            return False
        self.elapsed += max(delta_time, 0.0)
        progress = min(self.elapsed / self.duration, 1.0)
        self.x = self.start_x + (self.target_x - self.start_x) * progress
        self.y = self.start_y + (self.target_y - self.start_y) * progress
        self.active = progress < 1.0
        return self.active

    def render(self, mape: Mape) -> None:
        """Draw the pearl marker at its animated grid position.
        Center the transparent image over the current coordinates.
        made by: Mohammad Abu aresh
        """
        center = (
            round(mape.origin_x + self.x * Block.size),
            round(mape.origin_y + self.y * Block.size),
        )
        screen = pygame.display.get_surface()
        if screen is not None:
            screen.blit(self.image, self.image.get_rect(center=center))


class SlowPotion:
    def __init__(
        self,
        spawn_point: tuple[float, float],
        duration: float = 5.0,
    ) -> None:
        """Create a homing potion with a limited lifetime.
        Store the slowdown duration and transparent projectile image.
        made by: Mohammad Abu aresh
        """
        self.x, self.y = spawn_point
        self.duration = duration
        self.speed = 3.5
        self.lifetime = 5.0
        self.active = True
        size = (
            max(int(Block.size * 0.5), 1),
            max(int(Block.size * 0.75), 1),
        )
        self.image = pygame.transform.smoothscale(_POTION_IMAGE, size)

    def update(
        self,
        delta_time: float,
        grid: list[list[bool]],
        player: Player,
    ) -> None:
        """Guide the potion toward the player and apply a timed slow.
        Stop it at maze walls or when its lifetime expires.
        made by: Mohammad Abu aresh
        """
        if not self.active:
            return
        dt = max(delta_time, 0.0)
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.active = False
            return
        dx, dy = player.x - self.x, player.y - self.y
        distance = math.hypot(dx, dy)
        if distance <= 0.3:
            player.update_speed(35, self.duration)
            self.active = False
            return
        step = min(self.speed * dt, distance)
        next_x = self.x + dx / distance * step
        next_y = self.y + dy / distance * step
        if not _is_walkable(grid, next_x, next_y):
            self.active = False
            return
        self.x, self.y = next_x, next_y
        if math.hypot(player.x - self.x, player.y - self.y) <= 0.3:
            player.update_speed(35, self.duration)
            self.active = False

    def render(self, mape: Mape) -> None:
        """Draw the potion at its current grid position.
        Keep the bottle centered so it moves smoothly through corridors.
        made by: Mohammad Abu aresh
        """
        center = (
            round(mape.origin_x + self.x * Block.size),
            round(mape.origin_y + self.y * Block.size),
        )
        screen = pygame.display.get_surface()
        if screen is not None:
            screen.blit(self.image, self.image.get_rect(center=center))
