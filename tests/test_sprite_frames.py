import os
import unittest
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from game.block import Block  # noqa: E402
from game.creature import sprite_frames as frames_module  # noqa: E402
from game.creature.sprite_frames import (  # noqa: E402
    BLOCK_TOP_OFFSET,
    ENTITY_HEIGHTS,
    FRONT_WIDTH_CAP,
    GROUND_FRACTION,
    SIDE_WIDTH_CAP,
    FrameSet,
    Look,
    build_frames,
    feet_offset,
    frame_scale,
    frame_set,
    paste_position,
    sheet_size,
    tint_frame,
    view_scales,
)

STEVE_BOXES = {
    "": (95, 257, 506, 462),
    "_walking": (80, 286, 539, 431),
    "_up": (82, 277, 531, 441),
    "_up_walking": (65, 295, 539, 431),
    "_r_stoped": (135, 157, 497, 452),
    "_r_front": (91, 258, 496, 452),
    "_r_back": (74, 271, 495, 439),
}

ZOMBIE_BOXES = {
    "": (100, 260, 488, 460),
    "_walking": (100, 259, 493, 460),
    "_up": (106, 248, 488, 460),
    "_up_walking": (106, 248, 493, 460),
    "_r_stoped": (150, 262, 506, 460),
    "_r_front": (111, 302, 498, 460),
    "_r_back": (91, 320, 479, 460),
}

NAMES = (
    "", "_walking", "_up", "_up_walking",
    "_r_stoped", "_r_front", "_r_back",
)


class FrameGeometryTests(unittest.TestCase):
    def test_scale_makes_a_frame_the_target_height(self) -> None:
        """Verify the scale brings a frame to the requested height.
        A zero height frame must not divide by zero.
        made by: Mohammad Abu Aresh
        """
        self.assertAlmostEqual(frame_scale(100, 500), 0.2)
        self.assertGreater(frame_scale(100, 0), 0)

    def test_sheet_is_wide_enough_for_the_widest_frame(self) -> None:
        """Verify the common sheet holds every frame around its center.
        The farthest edge from the center decides the width.
        made by: Mohammad Abu Aresh
        """
        items = [
            ((100, 260, 488, 460), (0.2, 0.2)),
            ((91, 320, 479, 460), (0.2, 0.2)),
        ]
        width, height = sheet_size(items)
        self.assertEqual(width, 2 * 37)
        self.assertEqual(height, 98)

    def test_sheet_uses_both_axes_of_a_slimmed_frame(self) -> None:
        """Verify a slimmed frame is measured with its own two scales.
        The width follows the horizontal scale and the height the vertical.
        made by: Mohammad Abu Aresh
        """
        width, height = sheet_size([((100, 260, 500, 460), (0.1, 0.2))])
        self.assertEqual((width, height), (2 * 13, 100))

    def test_frames_keep_the_body_center_and_the_feet(self) -> None:
        """Verify a frame is pasted around the center with feet down.
        Check a narrow frame and a frame whose arms reach forward.
        made by: Mohammad Abu Aresh
        """
        size = (56, 98)
        narrow = paste_position((100, 260, 488, 460), size, (0.2, 0.2))
        self.assertEqual(
            narrow, (round(28 + (100 - 230) * 0.2), 98 - round(488 * 0.2))
        )
        reaching = paste_position((150, 262, 506, 460), size, (0.2, 0.2))
        self.assertEqual(reaching[1], 98 - round(506 * 0.2))

    def test_slimmed_frames_move_closer_to_the_center(self) -> None:
        """Verify the horizontal scale shrinks the distance to the center.
        The vertical scale only decides the feet position.
        made by: Mohammad Abu Aresh
        """
        spot = paste_position((100, 260, 500, 460), (60, 100), (0.1, 0.2))
        self.assertEqual(spot, (round(30 + (100 - 230) * 0.1), 0))


class FeetOffsetTests(unittest.TestCase):
    def test_fractions_follow_the_requested_sinking(self) -> None:
        """Verify how much of each body is hidden behind the block below.
        A fifth for the people, a quarter for the baby, a sixth for Enderman.
        made by: Mohammad Abu Aresh
        """
        self.assertEqual(GROUND_FRACTION["steve"], 0.2)
        self.assertEqual(GROUND_FRACTION["skeleton"], 0.2)
        self.assertEqual(GROUND_FRACTION["witch"], 0.2)
        self.assertEqual(GROUND_FRACTION["zombie"], 0.25)
        self.assertAlmostEqual(GROUND_FRACTION["enderman"], 1 / 6)

    def test_the_part_below_the_block_top_is_the_fraction_of_the_body(
        self
    ) -> None:
        """Verify the sunk part divided by the height is the fraction.
        Check every creature kind in the table.
        made by: Mohammad Abu Aresh
        """
        for kind, fraction in GROUND_FRACTION.items():
            sunk = feet_offset(kind) - BLOCK_TOP_OFFSET
            self.assertAlmostEqual(sunk / ENTITY_HEIGHTS[kind], fraction)

    def test_every_creature_has_a_size_and_a_fraction(self) -> None:
        """Verify both tables describe the same five creatures.
        A missing entry would break the sprite loading.
        made by: Mohammad Abu Aresh
        """
        self.assertEqual(set(GROUND_FRACTION), set(ENTITY_HEIGHTS))

    def test_the_tall_creature_sinks_less_than_the_others(self) -> None:
        """Verify the Enderman hides the smallest part of its body.
        Compare it with the people and the baby zombie.
        made by: Mohammad Abu Aresh
        """
        enderman = GROUND_FRACTION["enderman"]
        for kind in ("steve", "skeleton", "witch", "zombie"):
            self.assertLess(enderman, GROUND_FRACTION[kind])

    def test_feet_are_always_below_the_top_of_the_next_block(self) -> None:
        """Verify every creature sinks into the block under its cell.
        The feet offset must exceed the block top offset.
        made by: Mohammad Abu Aresh
        """
        for kind in GROUND_FRACTION:
            self.assertGreater(feet_offset(kind), BLOCK_TOP_OFFSET)


class ViewScaleTests(unittest.TestCase):
    def shown(
        self, boxes: Any, height: int, block: int
    ) -> dict[str, tuple[float, float]]:
        """Return the final width and height in pixels of every frame.
        Use the two scales chosen for the target height and block.
        made by: Mohammad Abu Aresh
        """
        scales = view_scales(boxes, height, block)
        return {
            name: (box[1] * scales[name][0], box[2] * scales[name][1])
            for name, box in boxes.items()
        }

    def test_minecraft_heights_are_used_for_every_creature(self) -> None:
        """Verify the entity heights follow the real Minecraft sizes.
        Steve is 1.8 blocks and both caps are one block or less.
        made by: Mohammad Abu Aresh
        """
        self.assertEqual(ENTITY_HEIGHTS["steve"], 1.8)
        self.assertEqual(ENTITY_HEIGHTS["zombie"], 0.975)
        self.assertEqual(ENTITY_HEIGHTS["skeleton"], 1.99)
        self.assertEqual(ENTITY_HEIGHTS["witch"], 1.95)
        self.assertEqual(ENTITY_HEIGHTS["enderman"], 2.9)
        self.assertEqual(FRONT_WIDTH_CAP, 0.75)
        self.assertEqual(SIDE_WIDTH_CAP, 1.0)

    def test_every_frame_keeps_exactly_the_target_height(self) -> None:
        """Verify slimming never changes the height of a frame.
        Check all seven frames of Steve with a block of sixty four.
        made by: Mohammad Abu Aresh
        """
        for name, (_, height) in self.shown(STEVE_BOXES, 115, 64).items():
            self.assertAlmostEqual(height, 115, msg=name)

    def test_steve_front_and_back_are_slimmed_to_the_cap(self) -> None:
        """Verify Steve is no wider than three quarters of a block.
        Check the four front and back frames.
        made by: Mohammad Abu Aresh
        """
        shown = self.shown(STEVE_BOXES, 115, 64)
        cap = 64 * FRONT_WIDTH_CAP
        for name in ("", "_walking", "_up", "_up_walking"):
            self.assertLessEqual(shown[name][0], cap + 1e-6, msg=name)
        names = ("", "_walking", "_up", "_up_walking")
        widest = max(shown[name][0] for name in names)
        self.assertAlmostEqual(widest, cap)

    def test_both_frames_of_a_view_share_the_slimming(self) -> None:
        """Verify the standing and walking frames keep their proportions.
        The width must not jump between the two steps of a view.
        made by: Mohammad Abu Aresh
        """
        scales = view_scales(STEVE_BOXES, 115, 64)
        self.assertAlmostEqual(
            scales[""][0] / scales[""][1],
            scales["_walking"][0] / scales["_walking"][1],
        )
        self.assertAlmostEqual(
            scales["_up"][0] / scales["_up"][1],
            scales["_up_walking"][0] / scales["_up_walking"][1],
        )

    def test_a_looser_cap_gives_a_wider_creature(self) -> None:
        """Verify the width follows the block size and the cap.
        A bigger block lets the same creature be wider.
        made by: Mohammad Abu Aresh
        """
        small = self.shown(STEVE_BOXES, 115, 64)[""][0]
        large = self.shown(STEVE_BOXES, 115, 128)[""][0]
        self.assertGreater(large, small)

    def test_wide_side_views_are_limited_to_one_block(self) -> None:
        """Verify strided side frames are no wider than a block.
        The three side frames share one slimming factor.
        made by: Mohammad Abu Aresh
        """
        boxes = {
            "_r_stoped": (0, 100, 500, 460),
            "_r_front": (0, 400, 500, 460),
            "_r_back": (0, 420, 500, 460),
        }
        shown = self.shown(boxes, 115, 64)
        self.assertAlmostEqual(shown["_r_back"][0], 64)
        scales = view_scales(boxes, 115, 64)
        ratios = {round(sx / sy, 6) for sx, sy in scales.values()}
        self.assertEqual(len(ratios), 1)

    def test_side_views_below_the_cap_are_not_changed(self) -> None:
        """Verify narrow side frames keep their natural proportions.
        Steve is narrower than a block from the side.
        made by: Mohammad Abu Aresh
        """
        scales = view_scales(STEVE_BOXES, 115, 64)
        for name in ("_r_stoped", "_r_front", "_r_back"):
            self.assertAlmostEqual(scales[name][0], scales[name][1])

    def test_narrow_creatures_are_not_slimmed(self) -> None:
        """Verify a creature that is already thin keeps its proportions.
        The zombie is far below the cap at its Minecraft height.
        made by: Mohammad Abu Aresh
        """
        scales = view_scales(ZOMBIE_BOXES, 62, 64)
        for name, (sx, sy) in scales.items():
            self.assertAlmostEqual(sx, sy, msg=name)


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
        frames: Any = {name: f"img{name}" for name in NAMES}
        with patch.object(frames_module, "pygame", fake):
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
        frames: Any = {name: f"img{name}" for name in NAMES}
        with patch.object(frames_module, "pygame", fake), patch.object(
            frames_module, "tint_frame", lambda image: ("tint", image)
        ):
            result = FrameSet(frames)
        self.assertEqual(result.normal.idle["down"], "img")
        self.assertEqual(result.tinted.idle["down"], ("tint", "img"))

    def test_frame_sets_are_cached_per_size(self) -> None:
        """Verify frames are rebuilt only when the height changes.
        Ask twice for one height and once for another.
        made by: Mohammad Abu Aresh
        """
        frames_module._CACHE.clear()
        self.addCleanup(frames_module._CACHE.clear)
        raw: Any = {"": "image"}
        with patch.object(
            frames_module, "build_frames", return_value={}
        ) as build, patch.object(
            frames_module, "FrameSet", lambda frames: "set"
        ):
            self.assertEqual(frame_set(raw, 80), "set")
            frame_set(raw, 80)
            frame_set(raw, 120)
        self.assertEqual(build.call_count, 2)

    def test_frame_sets_are_rebuilt_when_the_block_size_changes(self) -> None:
        """Verify a new block size rebuilds the frames for that block.
        The same height with another block size is a different set.
        made by: Mohammad Abu Aresh
        """
        frames_module._CACHE.clear()
        old = Block.size
        self.addCleanup(setattr, Block, "size", old)
        self.addCleanup(frames_module._CACHE.clear)
        raw: Any = {"": "image"}
        with patch.object(
            frames_module, "build_frames", return_value={}
        ) as build, patch.object(
            frames_module, "FrameSet", lambda frames: "set"
        ):
            Block.size = 40
            frame_set(raw, 80)
            Block.size = 60
            frame_set(raw, 80)
        self.assertEqual(build.call_args_list[0].args[2], 40)
        self.assertEqual(build.call_args_list[1].args[2], 60)

    def test_every_built_frame_shares_one_sheet_and_one_height(self) -> None:
        """Verify all frames get the same sheet size and the same height.
        Each frame is scaled by its own height to the requested one.
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

        raw: Any = {name: image(100, 260, 500) for name in NAMES}
        raw["_r_back"] = image(91, 320, 480)
        fake = SimpleNamespace(
            transform=SimpleNamespace(smoothscale=smooth),
            Surface=Sheet,
            SRCALPHA=1,
        )
        with patch.object(frames_module, "pygame", fake):
            frames: Any = build_frames(raw, 100, 1000)
        sizes = {sheet.size for sheet in frames.values()}
        self.assertEqual(len(sizes), 1)
        self.assertEqual(calls[0], (52, 100))
        self.assertEqual(calls[6], (67, 100))
        self.assertEqual(frames[""].pasted[0][1][1], 0)


class TintTests(unittest.TestCase):
    def test_tint_multiplies_then_adds_a_blue_color(self) -> None:
        """Verify the tint leans toward blue and keeps transparency.
        Check the two fills and the blend flags used for them.
        made by: Mohammad Abu Aresh
        """
        fills: list[Any] = []

        class Frame:
            def copy(self) -> Any:
                """Return the same fake frame as the copy.
                The test records the fills made on it.
                made by: Mohammad Abu Aresh
                """
                return self

            def fill(self, color: Any, special_flags: Any) -> None:
                """Record the color and the blend flag of a fill.
                The test reads the record afterwards.
                made by: Mohammad Abu Aresh
                """
                fills.append((color, special_flags))

        fake = SimpleNamespace(BLEND_RGBA_MULT="mult", BLEND_RGBA_ADD="add")
        with patch.object(frames_module, "pygame", fake):
            tint_frame(cast(Any, Frame()))
        self.assertEqual([flag for _, flag in fills], ["mult", "add"])
        multiply, add = fills[0][0], fills[1][0]
        self.assertGreater(multiply[2], multiply[0])
        self.assertGreater(multiply[2], multiply[1])
        self.assertGreater(add[2], add[0])
        self.assertEqual(multiply[3], 255)
        self.assertEqual(add[3], 0)


if __name__ == "__main__":
    unittest.main()
