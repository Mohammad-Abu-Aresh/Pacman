from __future__ import annotations
import math
from typing import TYPE_CHECKING
import pygame
from ..block import Block, Mape

if TYPE_CHECKING:
    from .creature import Control_creature

FEET_OFFSET = 1.3
STRIDE = 0.5
TELEPORT_DISTANCE = 1.5
TINT_MULTIPLY = (120, 150, 255, 255)
TINT_ADD = (10, 20, 60, 0)
RIGHT_CYCLE = ("_r_front", "_r_stoped", "_r_back", "_r_stoped")
FrameBox = tuple[int, int, int, int]


def facing_from_delta(dx: float, dy: float) -> str:
    """
    Choose the facing name from a movement in grid coordinates.
    Prefer the axis with the larger distance and use the screen axes.
    made by: Mohammad Abu Aresh
    """
    if abs(dx) >= abs(dy):
        return "right" if dx > 0 else "left"
    return "down" if dy > 0 else "up"


def frame_scale(target_height: float, reference_height: float) -> float:
    """
    Return the scale that makes the reference frame the target height.
    Use one scale for every frame so the creature never changes size.
    made by: Mohammad Abu Aresh
    """
    return target_height / max(reference_height, 1)


def sheet_size(boxes: list[FrameBox], scale: float) -> tuple[int, int]:
    """
    Compute the common size of all frames of one creature.
    Each box holds the left edge, width, height and canvas width.
    made by: Mohammad Abu Aresh
    """
    half = max(
        max(abs(left - canvas / 2), abs(left + width - canvas / 2))
        for left, width, _, canvas in boxes
    )
    height = max(box[2] for box in boxes)
    return 2 * math.ceil(half * scale), math.ceil(height * scale)


def paste_position(
    box: FrameBox, size: tuple[int, int], scale: float
) -> tuple[int, int]:
    """
    Compute where a cropped frame is placed on the common sheet.
    Keep the body center on the middle and the feet on the bottom.
    made by: Mohammad Abu Aresh
    """
    left, _, height, canvas = box
    x = size[0] / 2 + (left - canvas / 2) * scale
    return round(x), size[1] - round(height * scale)


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


def tint_frame(frame: pygame.Surface) -> pygame.Surface:
    """
    Return a copy of a frame that leans toward blue.
    Keep the transparency so only the visible pixels change color.
    made by: Mohammad Abu Aresh
    """
    tinted = frame.copy()
    tinted.fill(TINT_MULTIPLY, special_flags=pygame.BLEND_RGBA_MULT)
    tinted.fill(TINT_ADD, special_flags=pygame.BLEND_RGBA_ADD)
    return tinted


class Look:
    def __init__(self, frames: dict[str, pygame.Surface]) -> None:
        """
        Arrange the frames of one color into walking cycles.
        Build the left side by mirroring the right side frames.
        made by: Mohammad Abu Aresh
        """
        right = [frames[name] for name in RIGHT_CYCLE]
        left = [pygame.transform.flip(image, True, False) for image in right]
        self.cycles: dict[str, list[pygame.Surface]] = {
            "down": [frames[""], frames["_walking"]],
            "up": [frames["_up"], frames["_up_walking"]],
            "right": right,
            "left": left,
        }
        self.idle: dict[str, pygame.Surface] = {
            "down": frames[""],
            "up": frames["_up"],
            "right": frames["_r_stoped"],
            "left": left[1],
        }


class FrameSet:
    def __init__(self, frames: dict[str, pygame.Surface]) -> None:
        """
        Store the normal and the blue tinted look of a creature.
        Build both once so the game only picks frames afterwards.
        made by: Mohammad Abu Aresh
        """
        self.normal = Look(frames)
        self.tinted = Look(
            {name: tint_frame(image) for name, image in frames.items()}
        )


_CACHE: dict[tuple[int, int], FrameSet] = {}


def build_frames(
    raw: dict[str, pygame.Surface], height: int
) -> dict[str, pygame.Surface]:
    """
    Crop, scale and align the raw frames of one creature.
    Give every frame the same size with the feet on the bottom.
    made by: Mohammad Abu Aresh
    """
    rects = {
        name: image.get_bounding_rect(min_alpha=9)
        for name, image in raw.items()
    }
    boxes = {
        name: (rect.x, rect.w, rect.h, raw[name].get_width())
        for name, rect in rects.items()
    }
    scale = frame_scale(height, boxes[""][2])
    size = sheet_size(list(boxes.values()), scale)
    frames = {}
    for name, image in raw.items():
        box = boxes[name]
        part = pygame.transform.smoothscale(
            image.subsurface(rects[name]),
            (round(box[1] * scale), round(box[2] * scale)),
        )
        sheet = pygame.Surface(size, pygame.SRCALPHA)
        sheet.blit(part, paste_position(box, size, scale))
        frames[name] = sheet
    return frames


def frame_set(raw: dict[str, pygame.Surface], height: int) -> FrameSet:
    """
    Return the cached frame set for the given frames and height.
    Rebuild it only when the block size changes the height.
    made by: Mohammad Abu Aresh
    """
    key = (id(raw), height)
    if key not in _CACHE:
        _CACHE[key] = FrameSet(build_frames(raw, height))
    return _CACHE[key]


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
        controller.BabyZombie,
        controller.Skeleton,
        controller.Enderman,
        controller.witch,
    ):
        if monster.live:
            monster.image = monster.walk.update(
                monster.x, monster.y, monster.frightened
            )
