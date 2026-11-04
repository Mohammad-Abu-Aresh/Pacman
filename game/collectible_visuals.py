import math
import pygame


def create_diamond(size: int) -> pygame.Surface:
    """Create a faceted cyan diamond on a transparent surface.
    Scale its geometry to the supplied square size.
    made by: Mohammad Abu aresh
    """
    size = max(size, 8)
    center = size // 2
    points = [
        (center, 1), (size - 2, center),
        (center, size - 2), (1, center),
    ]
    image = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.polygon(image, (40, 190, 225), points)
    pygame.draw.polygon(
        image, (185, 250, 255),
        [(center, 1), (center, center), (1, center)],
    )
    pygame.draw.polygon(
        image, (20, 115, 175),
        [(center, center), (size - 2, center), (center, size - 2)],
    )
    pygame.draw.line(
        image, (240, 255, 255), (center, 2), (center, size - 2), 1
    )
    return image


def create_nether_star(size: int) -> pygame.Surface:
    """Create a pale cyan five-point Nether Star with a glowing core.
    Keep the star centered on a transparent square surface.
    made by: Mohammad Abu aresh
    """
    size = max(size, 12)
    center = size / 2
    outer = size * 0.48
    inner = size * 0.22
    points = []
    for index in range(10):
        radius = outer if index % 2 == 0 else inner
        angle = -math.pi / 2 + index * math.pi / 5
        points.append((
            round(center + math.cos(angle) * radius),
            round(center + math.sin(angle) * radius),
        ))
    image = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.polygon(image, (90, 195, 225), points)
    pygame.draw.polygon(
        image, (220, 255, 255),
        [
            (round(center), round(center - outer * 0.48)),
            (round(center + outer * 0.46), round(center + inner * 0.25)),
            (round(center - outer * 0.46), round(center + inner * 0.25)),
        ],
    )
    pygame.draw.circle(
        image, (245, 255, 255),
        (round(center), round(center)), max(size // 10, 1)
    )
    return image
