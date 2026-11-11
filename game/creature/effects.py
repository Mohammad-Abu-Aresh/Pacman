from __future__ import annotations
import pygame
from ..block import Block, Mape
from .player import Direction


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
    angles = {
        Direction.right: 0, Direction.up: 90,
        Direction.left: 180, Direction.down: 270,
    }
    return pygame.transform.rotate(image, angles.get(direction, 0))
