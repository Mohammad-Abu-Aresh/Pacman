from __future__ import annotations
import math
import pygame
from ..block import Block, Mape
from .player import Player


_SHEET = pygame.image.load("photos/abilities/hardcore_items.png")
_ARROW_IMAGE = _SHEET.subsurface((0, 0, 64, 64)).copy()
_PEARL_IMAGE = _SHEET.subsurface((64, 0, 64, 64)).copy()
_POTION_IMAGE = _SHEET.subsurface((128, 0, 64, 64)).copy()


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
        """Create an arrow with a normalized travel direction.
        Store its position, speed, lifetime, and transparent sprite.
        made by: Mohammad Abu aresh
        """
        self.x, self.y = spawn_point
        length = math.hypot(*direction) or 1.0
        self.direction = (direction[0] / length, direction[1] / length)
        self.speed = speed
        self.lifetime = 4.0
        self.active = True
        size = max(int(Block.size * 0.8), 1)
        self.image = pygame.transform.smoothscale(_ARROW_IMAGE, (size, size))

    def update(self, delta_time: float, grid: list[list[bool]]) -> None:
        """Advance the arrow until it hits a wall or expires.
        Move in short frame-time steps so the projectile cannot skip a cell.
        made by: Mohammad Abu aresh
        """
        dt = max(delta_time, 0.0)
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.active = False
            return
        next_x = self.x + self.direction[0] * self.speed * dt
        next_y = self.y + self.direction[1] * self.speed * dt
        if not _is_walkable(grid, next_x, next_y):
            self.active = False
            return
        self.x, self.y = next_x, next_y

    def hits_player(self, player: Player) -> bool:
        """Check whether the arrow overlaps the player's grid position.
        Use a small circular radius to avoid oversized hitboxes.
        made by: Mohammad Abu aresh
        """
        dx, dy = self.x - player.x, self.y - player.y
        return self.active and dx * dx + dy * dy <= 0.12

    def render(self, mape: Mape) -> None:
        """Draw the arrow rotated along its current travel direction.
        Position the transparent sprite in maze screen coordinates.
        made by: Mohammad Abu aresh
        """
        angle = math.degrees(
            math.atan2(-self.direction[1], self.direction[0])
        ) - 45
        image = pygame.transform.rotate(self.image, angle)
        center = (
            round(mape.origin_x + self.x * Block.size),
            round(mape.origin_y + self.y * Block.size),
        )
        Images_screen = pygame.display.get_surface()
        if Images_screen is not None:
            Images_screen.blit(image, image.get_rect(center=center))


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
        """Guide the potion toward the player and apply a timed slow on contact.
        Stop the projectile at maze walls or when its lifetime expires.
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
