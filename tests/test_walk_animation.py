import os
import unittest
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from game.block import Block  # noqa: E402
from game.creature import walk_animation as walk_module  # noqa: E402
from game.creature.walk_animation import (  # noqa: E402
    FrameSet,
    Look,
    WalkAnimation,
    anchored_rect,
    build_frames,
    facing_from_delta,
    frame_scale,
    frame_set,
    paste_position,
    sheet_size,
)

NAMES = (
    "", "_walking", "_up", "_up_walking",
    "_r_stoped", "_r_front", "_r_back",
)


def fake_look(tag: str) -> Any:
    """Build a look whose frames are readable strings.
    The tag tells the normal look apart from the tinted one.
    made by: Mohammad Abu Aresh
    """
    return SimpleNamespace(
        cycles={
            "down": [f"{tag}-stand", f"{tag}-walk"],
            "up": [f"{tag}-up", f"{tag}-up-walk"],
            "right": [f"{tag}-r1", f"{tag}-r0", f"{tag}-r2", f"{tag}-r0"],
            "left": [f"{tag}-l1", f"{tag}-l0", f"{tag}-l2", f"{tag}-l0"],
        },
        idle={
            "down": f"{tag}-stand", "up": f"{tag}-up",
            "right": f"{tag}-r0", "left": f"{tag}-l0",
        },
    )


def make_animation() -> WalkAnimation:
    """Create a walking animation on top of readable fake frames.
    Use one normal look and one tinted look.
    made by: Mohammad Abu Aresh
    """
    frames: Any = SimpleNamespace(
        normal=fake_look("n"), tinted=fake_look("t")
    )
    return WalkAnimation(frames)


def walk(
    animation: WalkAnimation, xs: list[float], y: float = 0.0
) -> list[Any]:
    """Move an animation through the given x positions on one row.
    Return the frame shown after every position.
    made by: Mohammad Abu Aresh
    """
    return [animation.update(x, y, False) for x in xs]


class GeometryTests(unittest.TestCase):
    def test_facing_follows_the_larger_axis(self) -> None:
        """Verify the facing name comes from the movement direction.
        Check the four screen directions and a stronger vertical move.
        made by: Mohammad Abu Aresh
        """
        self.assertEqual(facing_from_delta(0.3, 0), "right")
        self.assertEqual(facing_from_delta(-0.3, 0), "left")
        self.assertEqual(facing_from_delta(0, 0.3), "down")
        self.assertEqual(facing_from_delta(0, -0.3), "up")
        self.assertEqual(facing_from_delta(0.1, 0.4), "down")

    def test_one_scale_is_used_for_every_frame(self) -> None:
        """Verify the scale makes the reference frame the target height.
        A zero height reference must not divide by zero.
        made by: Mohammad Abu Aresh
        """
        self.assertAlmostEqual(frame_scale(100, 500), 0.2)
        self.assertGreater(frame_scale(100, 0), 0)

    def test_sheet_is_wide_enough_for_the_widest_frame(self) -> None:
        """Verify the common sheet holds every frame around its center.
        The farthest edge from the center decides the width.
        made by: Mohammad Abu Aresh
        """
        boxes = [(100, 260, 488, 460), (91, 320, 479, 460)]
        width, height = sheet_size(boxes, 0.2)
        self.assertEqual(width, 2 * 37)
        self.assertEqual(height, 98)

    def test_frames_keep_the_body_center_and_the_feet(self) -> None:
        """Verify a frame is pasted around the center with feet down.
        Check a narrow frame and a frame whose arms reach forward.
        made by: Mohammad Abu Aresh
        """
        size = (56, 98)
        narrow = paste_position((100, 260, 488, 460), size, 0.2)
        self.assertEqual(
            narrow, (round(28 + (100 - 230) * 0.2), 98 - round(488 * 0.2))
        )
        reaching = paste_position((150, 262, 506, 460), size, 0.2)
        self.assertEqual(reaching[1], 98 - round(506 * 0.2))

    def test_creature_stands_on_the_ground_line_of_its_cell(self) -> None:
        """Verify the image is centered on the cell with feet on the floor.
        Check the midbottom point for a cell at column two and row three.
        made by: Mohammad Abu Aresh
        """
        old = Block.size
        Block.size = 40
        self.addCleanup(setattr, Block, "size", old)
        image: Any = SimpleNamespace(get_rect=lambda **kwargs: kwargs)
        mape: Any = SimpleNamespace(origin_x=100, origin_y=50)
        rect: Any = anchored_rect(image, 2, 3, mape)
        expected = (100 + 3 * 40, int(50 + 4.3 * 40))
        self.assertEqual(rect["midbottom"], expected)


class WalkCycleTests(unittest.TestCase):
    def test_creature_stands_before_it_moves(self) -> None:
        """Verify the first frame is the standing front frame.
        Nothing has moved yet so no walking frame may appear.
        made by: Mohammad Abu Aresh
        """
        animation = make_animation()
        self.assertEqual(animation.update(5.0, 5.0, False), "n-stand")

    def test_right_walk_cycles_through_the_side_frames(self) -> None:
        """Verify walking right alternates front leg, stand and back leg.
        Check one full cycle and the wrap around to the first frame.
        made by: Mohammad Abu Aresh
        """
        animation = make_animation()
        shown = walk(animation, [0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
        self.assertEqual(
            shown, ["n-stand", "n-r1", "n-r0", "n-r0", "n-r2", "n-r0", "n-r1"]
        )

    def test_left_walk_uses_the_mirrored_frames(self) -> None:
        """Verify walking left shows the mirrored right frames.
        The facing must switch to left with the first step.
        made by: Mohammad Abu Aresh
        """
        animation = make_animation()
        shown = walk(animation, [3, 2.75, 2.5])
        self.assertEqual(shown, ["n-stand", "n-l1", "n-l0"])
        self.assertEqual(animation.facing, "left")

    def test_vertical_walks_use_front_and_back_views(self) -> None:
        """Verify going down shows the front view and up the back view.
        Both alternate between a standing and a walking frame.
        made by: Mohammad Abu Aresh
        """
        animation = make_animation()
        down = [animation.update(0, y, False) for y in (0, 0.25, 0.5)]
        self.assertEqual(down, ["n-stand", "n-stand", "n-walk"])
        up = [animation.update(0, y, False) for y in (0.25, 0.0)]
        self.assertEqual(up, ["n-up-walk", "n-up"])
        self.assertEqual(animation.facing, "up")

    def test_stopping_shows_the_idle_frame_of_the_last_facing(self) -> None:
        """Verify a creature that stops stands facing the same way.
        The walk phase restarts for the next movement.
        made by: Mohammad Abu Aresh
        """
        animation = make_animation()
        walk(animation, [0, 0.25, 0.5])
        self.assertEqual(animation.update(0.5, 0, False), "n-r0")
        self.assertEqual(animation.phase, 0.0)
        self.assertEqual(animation.update(0.75, 0, False), "n-r1")

    def test_teleport_is_not_a_walk(self) -> None:
        """Verify a big jump does not animate or turn the creature.
        Check a long jump after some normal steps.
        made by: Mohammad Abu Aresh
        """
        animation = make_animation()
        walk(animation, [0, 0.25])
        self.assertEqual(animation.update(8.0, 0, False), "n-r0")
        self.assertFalse(animation.moving)
        self.assertEqual(animation.facing, "right")

    def test_faster_creatures_change_frames_faster(self) -> None:
        """Verify the animation follows the distance moved.
        A creature moving twice as far advances twice as many frames.
        made by: Mohammad Abu Aresh
        """
        slow, fast = make_animation(), make_animation()
        walk(slow, [0, 0.1, 0.2, 0.3, 0.4])
        walk(fast, [0, 0.2, 0.4, 0.6, 0.8])
        self.assertAlmostEqual(fast.phase, 2 * slow.phase)

    def test_frightened_creatures_use_the_tinted_frames(self) -> None:
        """Verify the blue look replaces the normal look when scared.
        The same pose is shown, only with the tinted frames.
        made by: Mohammad Abu Aresh
        """
        animation = make_animation()
        animation.update(0, 0, False)
        self.assertEqual(animation.update(0.25, 0, True), "t-r1")
        self.assertEqual(animation.current(False), "n-r1")


class FrameBuildTests(unittest.TestCase):
    def test_left_side_is_the_mirror_of_the_right_side(self) -> None:
        """Verify the left frames are horizontal flips of the right ones.
        Check the cycle order and the idle left frame.
        made by: Mohammad Abu Aresh
        """
        fake = SimpleNamespace(
            transform=SimpleNamespace(
                flip=lambda image, x, y: ("flip", image, x, y)
            )
        )
        frames = {name: f"img{name}" for name in NAMES}
        with patch.object(walk_module, "pygame", fake):
            look = Look(frames)
        self.assertEqual(look.cycles["right"][0], "img_r_front")
        flipped = ("flip", "img_r_front", True, False)
        self.assertEqual(look.cycles["left"][0], flipped)
        stopped = ("flip", "img_r_stoped", True, False)
        self.assertEqual(look.idle["left"], stopped)
        self.assertEqual(look.cycles["down"], ["img", "img_walking"])
        self.assertEqual(look.cycles["up"], ["img_up", "img_up_walking"])

    def test_frame_set_builds_a_tinted_copy_of_every_frame(self) -> None:
        """Verify the tinted look is made from the same frames.
        Check that the standing front frame went through the tint.
        made by: Mohammad Abu Aresh
        """
        fake = SimpleNamespace(
            transform=SimpleNamespace(flip=lambda image, x, y: image)
        )
        frames = {name: f"img{name}" for name in NAMES}
        with patch.object(walk_module, "pygame", fake), patch.object(
            walk_module, "tint_frame", lambda image: ("tint", image)
        ):
            result = FrameSet(frames)
        self.assertEqual(result.normal.idle["down"], "img")
        self.assertEqual(result.tinted.idle["down"], ("tint", "img"))

    def test_frame_sets_are_cached_per_size(self) -> None:
        """Verify frames are rebuilt only when the height changes.
        Ask twice for one height and once for another.
        made by: Mohammad Abu Aresh
        """
        walk_module._CACHE.clear()
        self.addCleanup(walk_module._CACHE.clear)
        raw: Any = {"": "image"}
        with patch.object(
            walk_module, "build_frames", return_value={}
        ) as build, patch.object(
            walk_module, "FrameSet", lambda frames: "set"
        ):
            self.assertEqual(frame_set(raw, 80), "set")
            frame_set(raw, 80)
            frame_set(raw, 120)
        self.assertEqual(build.call_count, 2)

    def test_every_built_frame_shares_one_size_and_scale(self) -> None:
        """Verify all frames get the same sheet size and the same scale.
        The standing front frame decides the scale.
        made by: Mohammad Abu Aresh
        """
        calls: list[Any] = []

        class Sheet:
            def __init__(self, size: Any, flags: Any) -> None:
                """Remember the size and the pasted parts of a fake sheet.
                Stand in for a pygame surface that can be blitted on.
                made by: Mohammad Abu Aresh
                """
                self.size = size
                self.pasted: list[Any] = []

            def blit(self, part: Any, spot: Any) -> None:
                """Record which part was pasted at which position.
                The test reads the record afterwards.
                made by: Mohammad Abu Aresh
                """
                self.pasted.append((part, spot))

        def smooth(image: Any, size: Any) -> Any:
            """Record the requested scaled size and return a marker.
            The marker carries the size for later checks.
            made by: Mohammad Abu Aresh
            """
            calls.append(size)
            return ("scaled", size)

        def image(left: int, width: int, height: int) -> Any:
            """Create a fake raw frame with a given visible box.
            Every fake canvas is 460 pixels wide.
            made by: Mohammad Abu Aresh
            """
            rect = SimpleNamespace(x=left, w=width, h=height)
            return SimpleNamespace(
                get_bounding_rect=lambda min_alpha: rect,
                get_width=lambda: 460,
                subsurface=lambda r: ("crop", r),
            )

        raw: Any = {"": image(100, 260, 500), "_r_back": image(91, 320, 480)}
        fake = SimpleNamespace(
            transform=SimpleNamespace(smoothscale=smooth),
            Surface=Sheet,
            SRCALPHA=1,
        )
        with patch.object(walk_module, "pygame", fake):
            frames = build_frames(raw, 100)
        sizes = {sheet.size for sheet in frames.values()}
        self.assertEqual(len(sizes), 1)
        self.assertEqual(calls[0], (52, 100))
        self.assertEqual(frames[""].pasted[0][1][1], 0)


if __name__ == "__main__":
    unittest.main()
