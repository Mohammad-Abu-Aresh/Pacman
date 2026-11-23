from __future__ import annotations
import math
import pygame
from ..block import Block

FRONT_WIDTH_CAP = 0.75
SIDE_WIDTH_CAP = 1.0
ENTITY_HEIGHTS = {
    "steve": 1.8, "zombie": 0.975, "skeleton": 1.99,
    "witch": 1.95, "enderman": 2.9,
}
VIEW_CAPS = (
    (("", "_walking"), FRONT_WIDTH_CAP),
    (("_up", "_up_walking"), FRONT_WIDTH_CAP),
    (("_r_stoped", "_r_front", "_r_back"), SIDE_WIDTH_CAP),
)
TINT_MULTIPLY = (120, 150, 255, 255)
TINT_ADD = (10, 20, 60, 0)
RIGHT_CYCLE = ("_r_front", "_r_stoped", "_r_back", "_r_stoped")
FrameBox = tuple[int, int, int, int]
Scale = tuple[float, float]


def frame_scale(target_height: float, reference_height: float) -> float:
    """
    Return the scale that makes a frame the target height.
    Use it on every frame so the creature keeps one height.
    made by: Mohammad Abu Aresh
    """
    return target_height / max(reference_height, 1)


def view_scales(
    boxes: dict[str, FrameBox], height: float, block: int
) -> dict[str, Scale]:
    """
    Choose the horizontal and vertical scale of every frame.
    Keep one height and slim a view only when it is wider than its cap.
    made by: Mohammad Abu Aresh
    """
    heights = {n: frame_scale(height, box[2]) for n, box in boxes.items()}
    widths = dict(heights)
    for group, cap in VIEW_CAPS:
        names = [name for name in group if name in boxes]
        if names:
            widest = max(boxes[name][1] * widths[name] for name in names)
            for name in names:
                widths[name] *= min(1.0, cap * block / widest)
    return {name: (widths[name], heights[name]) for name in boxes}


def sheet_size(items: list[tuple[FrameBox, Scale]]) -> tuple[int, int]:
    """
    Compute the common size of all frames of one creature.
    Each item holds a box with its left edge, width, height and canvas
    made by: Mohammad Abu Aresh
    """
    half = max(
        max(abs(left - canvas / 2), abs(left + width - canvas / 2)) * scale[0]
        for (left, width, _, canvas), scale in items
    )
    height = max(box[2] * scale[1] for box, scale in items)
    return 2 * math.ceil(half), math.ceil(height)


def paste_position(
    box: FrameBox, size: tuple[int, int], scale: Scale
) -> tuple[int, int]:
    """
    Compute where a cropped frame is placed on the common sheet.
    Keep the body center on the middle and the feet on the bottom.
    made by: Mohammad Abu Aresh
    """
    left, _, height, canvas = box
    x = size[0] / 2 + (left - canvas / 2) * scale[0]
    return round(x), size[1] - round(height * scale[1])


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


_CACHE: dict[tuple[int, int, int], FrameSet] = {}


def build_frames(
    raw: dict[str, pygame.Surface], height: int, block: int
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
    scales = view_scales(boxes, height, block)
    size = sheet_size([(boxes[name], scales[name]) for name in boxes])
    frames: dict[str, pygame.Surface] = {}
    for name, image in raw.items():
        box, scale = boxes[name], scales[name]
        part = pygame.transform.smoothscale(
            image.subsurface(rects[name]),
            (round(box[1] * scale[0]), round(box[2] * scale[1])),
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
    key = (id(raw), height, Block.size)
    if key not in _CACHE:
        _CACHE[key] = FrameSet(build_frames(raw, height, Block.size))
    return _CACHE[key]
