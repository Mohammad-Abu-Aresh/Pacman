from __future__ import annotations
import random
import pygame
from photos.loderimages import Images
from ..block import Block, Mape

Color = tuple[int, int, int]
POTION_COLOR: Color = (140, 175, 235)
ENDER_COLOR: Color = (170, 60, 220)


def cell_center(mape: Mape, x: float, y: float) -> tuple[int, int]:
    """
    Convert a grid position to the screen pixel at its visual center.
    Use the map origin and the current block size.
    made by: Mohammad Abu Aresh
    """
    px = mape.origin_x + (x + 1.0) * Block.size
    py = mape.origin_y + (y + 0.8) * Block.size
    return int(px), int(py)


def render_rect(
    image: pygame.Surface, x: float, y: float, mape: Mape
) -> pygame.Rect:
    """
    Return an image rectangle centered on a grid position.
    Share one placement rule between arrows, potions and pearls.
    made by: Mohammad Abu Aresh
    """
    return image.get_rect(center=cell_center(mape, x, y))


def build_arrow_image(direction: tuple[int, int]) -> pygame.Surface:
    """
    Draw the arrow sprite with a shaft, a tip and a red tail.
    Rotate it by a multiple of 90 degrees to match the direction.
    made by: Mohammad Abu Aresh
    """
    length = max(Block.size * 9 // 10, 12)
    head = max(Block.size // 4, 6)
    image = pygame.Surface((length, head), pygame.SRCALPHA)
    shaft = pygame.Rect(0, head // 3, length - head, max(head // 3, 2))
    pygame.draw.rect(image, (120, 85, 40), shaft)
    tip = [(length - head, 0), (length, head // 2), (length - head, head)]
    pygame.draw.polygon(image, (205, 205, 210), tip)
    tail = pygame.Rect(0, head // 6, max(head // 3, 2), head * 2 // 3)
    pygame.draw.rect(image, (210, 60, 60), tail)
    angles = {(1, 0): 0, (0, -1): 90, (-1, 0): 180, (0, 1): 270}
    return pygame.transform.rotate(image, angles.get(direction, 0))


def build_flask_image() -> pygame.Surface:
    """
    Draw the slow potion flask with a glass neck and a shine.
    Scale the sprite from the current block size.
    made by: Mohammad Abu Aresh
    """
    size = max(Block.size // 2, 10)
    image = pygame.Surface((size, size), pygame.SRCALPHA)
    body = pygame.Rect(size // 6, size // 3, size * 2 // 3, size * 2 // 3)
    pygame.draw.rect(image, POTION_COLOR, body)
    pygame.draw.rect(image, (235, 240, 255), body, 1)
    neck = pygame.Rect(size * 3 // 8, 0, max(size // 4, 2), size // 3 + 1)
    pygame.draw.rect(image, (235, 240, 255), neck)
    shine = pygame.Rect(size // 4, size * 2 // 5, max(size // 7, 2), size // 4)
    pygame.draw.rect(image, (255, 255, 255), shine)
    return image


def build_pearl_image() -> pygame.Surface:
    """
    Draw the ender pearl as a dark disc with a bright core.
    Scale the sprite from the current block size.
    made by: Mohammad Abu Aresh
    """
    size = max(Block.size // 3, 8)
    image = pygame.Surface((size, size), pygame.SRCALPHA)
    center = (size // 2, size // 2)
    pygame.draw.circle(image, (25, 90, 80), center, size // 2)
    pygame.draw.circle(image, (80, 210, 170), center, max(size // 4, 2))
    return image


class Particle:
    def __init__(self, x: float, y: float, color: Color) -> None:
        """
        Create one particle with a random drift and lifetime.
        Store its start position and color in grid coordinates.
        made by: Mohammad Abu Aresh
        """
        self.x: float = x
        self.y: float = y
        self.vx: float = random.uniform(-1.5, 1.5)
        self.vy: float = random.uniform(-2.0, -0.5)
        self.life: float = random.uniform(0.4, 0.8)
        self.color: Color = color

    def update(self, delta_time: float) -> None:
        """
        Move the particle by its velocity and reduce its lifetime.
        Use the elapsed frame time in seconds.
        made by: Mohammad Abu Aresh
        """
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time
        self.life -= delta_time


class ParticleEffects:
    TRAIL_INTERVAL: float = 0.1

    def __init__(self) -> None:
        """
        Create the empty particle list and the trail timer.
        The list is drawn and updated by the owning controller.
        made by: Mohammad Abu Aresh
        """
        self.particles: list[Particle] = []
        self.trail_timer: float = 0.0

    def burst(
        self, x: float, y: float, color: Color, count: int = 14
    ) -> None:
        """
        Spawn a group of particles at one grid position.
        Use it for impacts, teleports and spawn effects.
        made by: Mohammad Abu Aresh
        """
        self.particles.extend(Particle(x, y, color) for _ in range(count))

    def trail(
        self, x: float, y: float, color: Color, delta_time: float
    ) -> None:
        """
        Emit one particle at a fixed interval while an effect lasts.
        Use it to show that the player is still slowed.
        made by: Mohammad Abu Aresh
        """
        self.trail_timer -= delta_time
        if self.trail_timer <= 0:
            self.trail_timer = self.TRAIL_INTERVAL
            self.particles.append(Particle(x, y, color))

    def update(self, delta_time: float) -> None:
        """
        Move every particle and remove the expired ones.
        Use the elapsed frame time in seconds.
        made by: Mohammad Abu Aresh
        """
        for particle in self.particles:
            particle.update(delta_time)
        self.particles = [p for p in self.particles if p.life > 0]

    def clear(self) -> None:
        """
        Remove all particles and reset the trail timer.
        Use it when the monsters are reset after a player death.
        made by: Mohammad Abu Aresh
        """
        self.particles.clear()
        self.trail_timer = 0.0

    def draw(self, mape: Mape) -> None:
        """
        Draw every particle as a small colored square on the screen.
        Convert grid positions with the shared cell center helper.
        made by: Mohammad Abu Aresh
        """
        side = max(Block.size // 8, 3)
        for particle in self.particles:
            x, y = cell_center(mape, particle.x, particle.y)
            rect = pygame.Rect(x, y, side, side)
            pygame.draw.rect(Images.screen, particle.color, rect)
