import os
import unittest
from types import SimpleNamespace
from typing import Any

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from game.block import Block  # noqa: E402
from game.creature.babyzombie import BabyZombie  # noqa: E402
from game.creature.player import Player  # noqa: E402
from game.creature.skeleton import Skeleton  # noqa: E402
from game.creature.witch import Witch  # noqa: E402


def make_player(x: float, y: float) -> Player:
    player = Player.__new__(Player)
    player.x = x
    player.y = y
    player.speed = 0.1
    player._normal_speed = 0.1
    player._slow_left = 0.0
    return player


def open_lane() -> Any:
    width = 42
    rows = ["#" * width, "#" + "." * (width - 2) + "#", "#" * width]
    return SimpleNamespace(
        every_cell=[[char == "#" for char in row] for row in rows]
    )


class SuperAbilityTests(unittest.TestCase):
    def setUp(self) -> None:
        Block.size = 40

    def test_zombie_is_fast_only_in_hardcore_outside_super(self) -> None:
        zombie = BabyZombie((1, 1), True)
        zombie.sync_super_speed(False)
        self.assertEqual(zombie.speed, 110)
        zombie.sync_super_speed(True)
        self.assertEqual(zombie.speed, 65)
        zombie.sync_super_speed(False)
        self.assertEqual(zombie.speed, 110)

    def test_zombie_stays_normal_without_hardcore(self) -> None:
        zombie = BabyZombie((1, 1), False)
        zombie.sync_super_speed(False)
        self.assertEqual(zombie.speed, 65)

    def test_skeleton_neither_shoots_nor_hits_during_super(self) -> None:
        skeleton = Skeleton((1, 1), True)
        mape = open_lane()
        player: Any = SimpleNamespace(x=10, y=1)
        skeleton.update_arrows(player, mape, 1 / 60, False)
        self.assertEqual(skeleton.active_arrows, [])
        skeleton.update_arrows(player, mape, 1 / 60)
        self.assertEqual(len(skeleton.active_arrows), 1)
        hits = [
            skeleton.update_arrows(player, mape, 1 / 60, False)
            for _ in range(60)
        ]
        self.assertNotIn(True, hits)
        self.assertFalse(skeleton.active_arrows[0].hit_player)

    def test_witch_does_not_throw_during_super(self) -> None:
        witch = Witch((5, 5), True)
        player = make_player(6, 5)
        witch.update_potion(player, 1 / 60, False)
        self.assertEqual(player.speed, 0.1)
        witch.update_potion(player, 1 / 60, True)
        self.assertAlmostEqual(player.speed, 0.035)


if __name__ == "__main__":
    unittest.main()
