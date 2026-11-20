import os
import unittest
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from game.block import Block  # noqa: E402
from game.creature import babyzombie as zombie_module  # noqa: E402
from game.creature import enderman as enderman_module  # noqa: E402
from game.creature import skeleton as skeleton_module  # noqa: E402
from game.creature import witch as witch_module  # noqa: E402
from game.creature.babyzombie import BabyZombie  # noqa: E402
from game.creature.enderman import Enderman  # noqa: E402
from game.creature.ghost_state import (  # noqa: E402
    set_monster_frightened_visual,
)
from game.creature.skeleton import Skeleton  # noqa: E402
from game.creature.walk_animation import (  # noqa: E402
    WalkAnimation,
    animate_creatures,
)
from game.creature.witch import Witch  # noqa: E402


def fake_frames() -> Any:
    """Build a frame set whose frames are readable strings.
    It holds a normal look and a tinted look.
    made by: Mohammad Abu Aresh
    """
    def look(tag: str) -> Any:
        """Build one look of readable frames.
        The tag tells the two looks apart.
        made by: Mohammad Abu Aresh
        """
        cycle = [f"{tag}-a", f"{tag}-b"]
        cycles = {"down": cycle, "up": cycle, "left": cycle, "right": cycle}
        idle = {name: f"{tag}-idle" for name in cycles}
        return SimpleNamespace(cycles=cycles, idle=idle)

    return SimpleNamespace(normal=look("n"), tinted=look("t"))


class MonsterSizeTests(unittest.TestCase):
    def setUp(self) -> None:
        """Set a block size of forty pixels for the height math.
        Restore the real block size after every test.
        made by: Mohammad Abu Aresh
        """
        self.old_size = Block.size
        Block.size = 40
        self.addCleanup(setattr, Block, "size", self.old_size)

    def build(self, module: Any, kind: Any) -> tuple[Any, Any]:
        """Create a monster while the frame builder is a recording mock.
        Return the monster and the mock to read the requested height.
        made by: Mohammad Abu Aresh
        """
        with patch.object(
            module, "frame_set", return_value=fake_frames()
        ) as builder:
            return kind((1, 1), True), builder

    def test_zombie_is_less_than_one_block_tall(self) -> None:
        """Verify the baby zombie keeps its small height of 0.9 block.
        Check the requested height and the first frame shown.
        made by: Mohammad Abu Aresh
        """
        monster, builder = self.build(zombie_module, BabyZombie)
        self.assertEqual(builder.call_args.args[1], 36)
        self.assertEqual(monster.image, "n-idle")

    def test_skeleton_is_one_and_eight_tenths_blocks_tall(self) -> None:
        """Verify the skeleton height is 1.8 blocks.
        The height decides the scale of every frame.
        made by: Mohammad Abu Aresh
        """
        monster, builder = self.build(skeleton_module, Skeleton)
        self.assertEqual(builder.call_args.args[1], 72)

    def test_witch_is_one_and_eight_tenths_blocks_tall(self) -> None:
        """Verify the witch height is 1.8 blocks.
        The height decides the scale of every frame.
        made by: Mohammad Abu Aresh
        """
        monster, builder = self.build(witch_module, Witch)
        self.assertEqual(builder.call_args.args[1], 72)

    def test_enderman_is_two_and_eight_tenths_blocks_tall(self) -> None:
        """Verify the Enderman height is 2.8 blocks.
        The height decides the scale of every frame.
        made by: Mohammad Abu Aresh
        """
        monster, builder = self.build(enderman_module, Enderman)
        self.assertEqual(builder.call_args.args[1], 112)

    def test_every_monster_stands_on_the_same_ground_line(self) -> None:
        """Verify all monsters are anchored by their feet at one height.
        Check the midbottom point of a skeleton and a zombie.
        made by: Mohammad Abu Aresh
        """
        mape: Any = SimpleNamespace(origin_x=100, origin_y=50)
        points = []
        for module, kind in (
            (skeleton_module, Skeleton), (zombie_module, BabyZombie)
        ):
            monster, _ = self.build(module, kind)
            monster.image = SimpleNamespace(get_rect=lambda **kw: kw)
            points.append(monster.get_render_rect(mape)["midbottom"])
        self.assertEqual(points[0], points[1])
        self.assertEqual(points[0], (100 + 2 * 40, int(50 + 2.3 * 40)))


class AnimateCreaturesTests(unittest.TestCase):
    def monster(self, live: bool, frightened: bool) -> Any:
        """Create a light monster with a recording walk animation.
        The animation returns a marker built from its arguments.
        made by: Mohammad Abu Aresh
        """
        walk = SimpleNamespace(
            update=lambda x, y, tinted: ("frame", x, y, tinted)
        )
        return SimpleNamespace(
            live=live, frightened=frightened, x=1.0, y=2.0,
            walk=walk, image="old",
        )

    def controller(self, **flags: Any) -> Any:
        """Build a controller whose four monsters follow the given flags.
        A monster missing from the flags is alive and not frightened.
        made by: Mohammad Abu Aresh
        """
        names = ("BabyZombie", "Skeleton", "Enderman", "witch")
        return SimpleNamespace(**{
            name: self.monster(*flags.get(name, (True, False)))
            for name in names
        })

    def test_live_monsters_get_their_next_frame(self) -> None:
        """Verify every live monster shows the frame of its position.
        Check all four monsters in one call.
        made by: Mohammad Abu Aresh
        """
        controller = self.controller()
        animate_creatures(controller)
        for name in ("BabyZombie", "Skeleton", "Enderman", "witch"):
            self.assertEqual(
                getattr(controller, name).image, ("frame", 1.0, 2.0, False)
            )

    def test_frightened_monsters_ask_for_the_blue_look(self) -> None:
        """Verify the frightened flag selects the tinted frames.
        The other monsters keep the normal look.
        made by: Mohammad Abu Aresh
        """
        controller = self.controller(Skeleton=(True, True))
        animate_creatures(controller)
        self.assertEqual(controller.Skeleton.image[3], True)
        self.assertEqual(controller.witch.image[3], False)

    def test_eaten_monsters_keep_their_eyes_sprite(self) -> None:
        """Verify a dead monster is not animated.
        Its eyes only sprite must stay until the respawn.
        made by: Mohammad Abu Aresh
        """
        controller = self.controller(Enderman=(False, False))
        animate_creatures(controller)
        self.assertEqual(controller.Enderman.image, "old")

    def test_real_animation_object_works_with_the_helper(self) -> None:
        """Verify a real walk animation can drive a monster image.
        Move the monster and check the frame changes from the idle one.
        made by: Mohammad Abu Aresh
        """
        monster = self.monster(True, False)
        monster.walk = WalkAnimation(fake_frames())
        controller = self.controller()
        controller.Skeleton = monster
        animate_creatures(controller)
        self.assertEqual(monster.image, "n-idle")
        monster.x += 0.25
        animate_creatures(controller)
        self.assertEqual(monster.image, "n-a")


class FrightenedLookTests(unittest.TestCase):
    def monster(self) -> Any:
        """Create a light monster that owns a real walk animation.
        The frames are readable strings with a normal and a tinted look.
        made by: Mohammad Abu Aresh
        """
        return SimpleNamespace(
            walk=WalkAnimation(fake_frames()), image="old"
        )

    def test_fear_switches_to_the_blue_look(self) -> None:
        """Verify a frightened monster shows the tinted frame.
        The pose stays the same and only the color changes.
        made by: Mohammad Abu Aresh
        """
        monster = self.monster()
        set_monster_frightened_visual(monster, True)
        self.assertEqual(monster.image, "t-idle")

    def test_end_of_fear_restores_the_normal_look(self) -> None:
        """Verify a calm monster shows the normal frame again.
        Switch the fear on and off.
        made by: Mohammad Abu Aresh
        """
        monster = self.monster()
        set_monster_frightened_visual(monster, True)
        set_monster_frightened_visual(monster, False)
        self.assertEqual(monster.image, "n-idle")

    def test_walking_frightened_monster_stays_blue(self) -> None:
        """Verify the animation keeps the tint while the monster flees.
        Walk a few steps and read the frame after each one.
        made by: Mohammad Abu Aresh
        """
        monster = self.monster()
        monster.live, monster.frightened = True, True
        monster.x, monster.y = 0.0, 0.0
        controller = SimpleNamespace(
            BabyZombie=monster, Skeleton=monster,
            Enderman=monster, witch=monster,
        )
        shown = []
        for step in range(4):
            monster.x = step * 0.25
            animate_creatures(controller)
            shown.append(monster.image)
        self.assertTrue(all(frame.startswith("t-") for frame in shown))


if __name__ == "__main__":
    unittest.main()
