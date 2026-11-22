from __future__ import annotations
import math
from typing import TYPE_CHECKING
import pygame
from ..block import Block, Mape
from .sprite_frames import FrameSet

if TYPE_CHECKING:
    from .creature import Control_creature

FEET_OFFSET = 1.3
STRIDE = 0.5
TELEPORT_DISTANCE = 1.5


def facing_from_delta(dx: float, dy: float) -> str:
    """
    Choose the facing name from a movement in grid coordinates.
    Prefer the axis with the larger distance and use the screen axes.
    made by: Mohammad Abu Aresh
    """
    if abs(dx) >= abs(dy):
        return "right" if dx > 0 else "left"
    return "down" if dy > 0 else "up"


def anchored_rect(
    image: pygame.Surface, x: float, y: float, mape: Mape
) -> pygame.Rect:
    """
    Return the rectangle that stands the image on its grid cell.
    Center it horizontally and put its feet on the cell ground line.
    made by: Mohammad Abu Aresh
    """
    px = mape.origin_x + (x + 1.0) * Block.size
    py = mape.origin_y + (y + FEET_OFFSET) * Block.size
    return image.get_rect(midbottom=(int(px), int(py)))


class WalkAnimation:
    def __init__(self, frames: FrameSet) -> None:
        """
        Start a walking animation that faces the camera and stands.
        Keep only the small state that changes while walking.
        made by: Mohammad Abu Aresh
        """
        self.frames = frames
        self.facing = "down"
        self.phase = 0.0
        self.moving = False
        self.last: tuple[float, float] | None = None

    def current(self, tinted: bool) -> pygame.Surface:
        """
        Return the frame to show right now without advancing it.
        Stand still when the creature is not moving.
        made by: Mohammad Abu Aresh
        """
        look = self.frames.tinted if tinted else self.frames.normal
        if not self.moving:
            return look.idle[self.facing]
        cycle = look.cycles[self.facing]
        return cycle[int(self.phase) % len(cycle)]

    def update(self, x: float, y: float, tinted: bool) -> pygame.Surface:
        """
        Advance the walk by the distance moved since the last call.
        Ignore jumps such as teleports and return the frame to show.
        made by: Mohammad Abu Aresh
        """
        self.moving = False
        if self.last is not None:
            dx, dy = x - self.last[0], y - self.last[1]
            distance = math.hypot(dx, dy)
            if 0 < distance <= TELEPORT_DISTANCE:
                self.facing = facing_from_delta(dx, dy)
                self.phase += distance / STRIDE
                self.moving = True
        if not self.moving:
            self.phase = 0.0
        self.last = (x, y)
        return self.current(tinted)


def animate_creatures(controller: Control_creature) -> None:
    """
    Show the next walking frame of Steve and every live monster.
    Eaten monsters keep their eyes only sprite until they respawn.
    made by: Mohammad Abu Aresh
    """
    player = controller.player
    player.image = player.walk.update(player.x, player.y, False)
    for monster in (
        controller.BabyZombie, controller.Skeleton,
        controller.Enderman, controller.witch,
    ):
        if monster.live:
            monster.image = monster.walk.update(
                monster.x, monster.y, monster.frightened
            )
