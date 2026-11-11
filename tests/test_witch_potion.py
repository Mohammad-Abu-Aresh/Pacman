import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from game.block import Block  # noqa: E402
from game.creature.player import Player  # noqa: E402
from game.creature.witch import Witch  # noqa: E402


def make_player(x: float, y: float) -> Player:
    player = Player.__new__(Player)
    player.x = x
    player.y = y
    player.speed = 0.1
    player._normal_speed = 0.1
    player._slow_left = 0.0
    return player


class WitchPotionTests(unittest.TestCase):
    def setUp(self) -> None:
        Block.size = 40
        self.witch = Witch((5, 5), True)

    def test_slows_player_inside_radius(self) -> None:
        player = make_player(7, 5)
        self.assertTrue(self.witch.throw_slow_potion(player))
        self.assertAlmostEqual(player.speed, 0.035)

    def test_ignores_player_outside_radius(self) -> None:
        player = make_player(20, 5)
        self.assertFalse(self.witch.throw_slow_potion(player))
        self.assertEqual(player.speed, 0.1)

    def test_inactive_outside_hardcore_or_when_dead(self) -> None:
        player = make_player(6, 5)
        self.witch.is_hardcore = False
        self.assertFalse(self.witch.throw_slow_potion(player))
        self.witch.is_hardcore = True
        self.witch.live = False
        self.assertFalse(self.witch.throw_slow_potion(player))
        self.assertEqual(player.speed, 0.1)

    def test_slow_expires_after_duration(self) -> None:
        player = make_player(6, 5)
        self.witch.throw_slow_potion(player)
        player.update_slow(4.9)
        self.assertAlmostEqual(player.speed, 0.035)
        player.update_slow(0.2)
        self.assertEqual(player.speed, 0.1)

    def test_repeated_potion_does_not_stack(self) -> None:
        player = make_player(6, 5)
        self.witch.throw_slow_potion(player)
        self.witch.throw_slow_potion(player)
        self.assertAlmostEqual(player.speed, 0.035)
        player.update_slow(6.0)
        self.assertEqual(player.speed, 0.1)

    def test_cooldown_blocks_second_throw(self) -> None:
        player = make_player(6, 5)
        self.witch.update_potion(player, 1 / 60)
        self.assertEqual(self.witch.potion_timer, self.witch.potion_cooldown)
        player.update_slow(10.0)
        self.witch.update_potion(player, 29.0)
        self.assertEqual(player.speed, 0.1)
        self.witch.update_potion(player, 1.5)
        self.assertAlmostEqual(player.speed, 0.035)


if __name__ == "__main__":
    unittest.main()
