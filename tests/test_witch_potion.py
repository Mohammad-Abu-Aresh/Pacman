import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from game.block import Block  # noqa: E402
from game.creature.abilities import SlowPotion  # noqa: E402
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


def land(witch: Witch, player: Player, frames: int = 60) -> int:
    landings = 0
    for _ in range(frames):
        landings += witch.update_potion(player, 1 / 60)
    return landings


class WitchPotionTests(unittest.TestCase):
    def setUp(self) -> None:
        Block.size = 40
        self.witch = Witch((5, 5), True)

    def throw(self, player: Player) -> None:
        self.witch.throw_slow_potion(player)
        self.witch.potion_timer = self.witch.potion_cooldown

    def test_throw_creates_flying_potion_without_slowing_yet(self) -> None:
        player = make_player(7, 5)
        self.assertTrue(self.witch.throw_slow_potion(player))
        self.assertEqual(len(self.witch.potions), 1)
        self.assertEqual(player.speed, 0.1)

    def test_potion_homes_in_and_slows_on_landing(self) -> None:
        player = make_player(7, 5)
        self.throw(player)
        self.assertEqual(land(self.witch, player), 1)
        self.assertAlmostEqual(player.speed, 0.035)
        self.assertTrue(player.is_slowed)
        self.assertEqual(self.witch.potions, [])

    def test_player_cannot_dodge_by_moving_away(self) -> None:
        player = make_player(7, 5)
        self.throw(player)
        landings = 0
        for _ in range(120):
            player.x += 0.05
            landings += self.witch.update_potion(player, 1 / 60)
        self.assertEqual(landings, 1)
        self.assertAlmostEqual(player.speed, 0.035)

    def test_ignores_player_outside_radius(self) -> None:
        player = make_player(20, 5)
        self.assertFalse(self.witch.throw_slow_potion(player))
        self.assertEqual(self.witch.potions, [])

    def test_inactive_outside_hardcore_or_when_dead(self) -> None:
        player = make_player(6, 5)
        self.witch.is_hardcore = False
        self.assertFalse(self.witch.throw_slow_potion(player))
        self.witch.is_hardcore = True
        self.witch.live = False
        self.assertFalse(self.witch.throw_slow_potion(player))
        self.assertEqual(self.witch.potions, [])

    def test_slow_expires_after_duration(self) -> None:
        player = make_player(6, 5)
        self.throw(player)
        land(self.witch, player)
        player.update_slow(4.9)
        self.assertAlmostEqual(player.speed, 0.035)
        player.update_slow(0.2)
        self.assertEqual(player.speed, 0.1)
        self.assertFalse(player.is_slowed)

    def test_repeated_potion_does_not_stack(self) -> None:
        player = make_player(6, 5)
        SlowPotion((5, 5)).apply_effect(player)
        SlowPotion((5, 5)).apply_effect(player)
        self.assertAlmostEqual(player.speed, 0.035)
        player.update_slow(6.0)
        self.assertEqual(player.speed, 0.1)

    def test_cooldown_blocks_second_throw(self) -> None:
        player = make_player(6, 5)
        self.witch.update_potion(player, 1 / 60)
        self.assertEqual(self.witch.potion_timer, self.witch.potion_cooldown)
        land(self.witch, player)
        player.update_slow(10.0)
        self.witch.update_potion(player, 29.0)
        self.assertEqual(self.witch.potions, [])
        self.witch.update_potion(player, 1.5)
        self.assertEqual(len(self.witch.potions), 1)

    def test_reset_clears_flying_potions(self) -> None:
        self.witch.throw_slow_potion(make_player(6, 5))
        self.witch.reset_ai()
        self.assertEqual(self.witch.potions, [])


if __name__ == "__main__":
    unittest.main()
