from __future__ import annotations
import random
import pygame
from photos.loderimages import Images
from ..block import Block, Mape

Color = tuple[int, int, int]
POTION_COLOR: Color = (140, 175, 235)


def cell_center(mape: Mape, x: float, y: float) -> tuple[int, int]:
    px = mape.origin_x + (x + 1.0) * Block.size
    py = mape.origin_y + (y + 0.8) * Block.size
    return int(px), int(py)


def render_rect(
    image: pygame.Surface, x: float, y: float, mape: Mape
) -> pygame.Rect:
    return image.get_rect(center=cell_center(mape, x, y))


def build_arrow_image(direction: tuple[int, int]) -> pygame.Surface:
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


class Particle:
    def __init__(self, x: float, y: float, color: Color) -> None:
        self.x: float = x
        self.y: float = y
        self.vx: float = random.uniform(-1.5, 1.5)
        self.vy: float = random.uniform(-2.0, -0.5)
        self.life: float = random.uniform(0.4, 0.8)
        self.color: Color = color

    def update(self, delta_time: float) -> None:
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time
        self.life -= delta_time


class ParticleEffects:
    TRAIL_INTERVAL: float = 0.1

    def __init__(self) -> None:
        self.particles: list[Particle] = []
        self.trail_timer: float = 0.0

    def burst(
        self, x: float, y: float, color: Color, count: int = 14
    ) -> None:
        self.particles.extend(Particle(x, y, color) for _ in range(count))

    def trail(
        self, x: float, y: float, color: Color, delta_time: float
    ) -> None:
        self.trail_timer -= delta_time
        if self.trail_timer <= 0:
            self.trail_timer = self.TRAIL_INTERVAL
            self.particles.append(Particle(x, y, color))

    def update(self, delta_time: float) -> None:
        for particle in self.particles:
            particle.update(delta_time)
        self.particles = [p for p in self.particles if p.life > 0]

    def clear(self) -> None:
        self.particles.clear()
        self.trail_timer = 0.0

    def draw(self, mape: Mape) -> None:
        side = max(Block.size // 8, 3)
        for particle in self.particles:
            x, y = cell_center(mape, particle.x, particle.y)
            rect = pygame.Rect(x, y, side, side)
            pygame.draw.rect(Images.screen, particle.color, rect)
