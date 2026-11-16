import os
import unittest
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from game.block import Block  # noqa: E402
from game.creature.abilities import SlowPotion  # noqa: E402
from game.creature.player import Player  # noqa: E402
from game.creature.witch import Witch  # noqa: E402


def make_player(x: float, y: float) -> Player:
    """Create a player object without running its constructor.
    Set only the fields used by the slow potion logic.
    made by: Mohammad Abu Aresh
    """
    player = Player.__new__(Player)
    player.x = x
    player.y = y
    player.speed = 0.1
    player._normal_speed = 0.1
    player._slow_left = 0.0
    return player


def land(witch: Witch, player: Player, frames: int = 60) -> int:
    """Update the witch for a number of frames.
    Return how many potions landed on the player.
    made by: Mohammad Abu Aresh
    """
    landings = 0
    for _ in range(frames):
        landings += witch.update_potion(player, 1 / 60)
    return landings


class WitchPotionTests(unittest.TestCase):
    def setUp(self) -> None:
        """Prepare a hardcore witch on a fixed block size.
        Every potion test starts from this witch.
        made by: Mohammad Abu Aresh
        """
        Block.size = 40
        self.witch = Witch((5, 5), True)

    def throw(self, player: Player) -> None:
        """Throw a potion and start the cooldown like the game does.
        It prevents an automatic second throw during the test.
        made by: Mohammad Abu Aresh
        """
        self.witch.throw_slow_potion(player)
        self.witch.potion_timer = self.witch.potion_cooldown

    def test_throw_creates_flying_potion_without_slowing_yet(self) -> None:
        """Verify a thrown potion starts flying without any effect.
        The player speed must stay unchanged until it lands.
        made by: Mohammad Abu Aresh
        """
        player = make_player(7, 5)
        self.assertTrue(self.witch.throw_slow_potion(player))
        self.assertEqual(len(self.witch.potions), 1)
        self.assertEqual(player.speed, 0.1)

    def test_potion_homes_in_and_slows_on_landing(self) -> None:
        """Verify the potion reaches the player and slows him.
        Check the slowed flag and the removed potion.
        made by: Mohammad Abu Aresh
        """
        player = make_player(7, 5)
        self.throw(player)
        self.assertEqual(land(self.witch, player), 1)
        self.assertAlmostEqual(player.speed, 0.035)
        self.assertTrue(player.is_slowed)
        self.assertEqual(self.witch.potions, [])

    def test_player_cannot_dodge_by_moving_away(self) -> None:
        """Verify a moving player cannot dodge the potion.
        The potion follows him and lands exactly once.
        made by: Mohammad Abu Aresh
        """
        player = make_player(7, 5)
        self.throw(player)
        landings = 0
        for _ in range(120):
            player.x += 0.05
            landings += self.witch.update_potion(player, 1 / 60)
        self.assertEqual(landings, 1)
        self.assertAlmostEqual(player.speed, 0.035)

    def test_ignores_player_outside_radius(self) -> None:
        """Verify a distant player is never targeted.
        No potion may be created.
        made by: Mohammad Abu Aresh
        """
        player = make_player(20, 5)
        self.assertFalse(self.witch.throw_slow_potion(player))
        self.assertEqual(self.witch.potions, [])

    def test_inactive_outside_hardcore_or_when_dead(self) -> None:
        """Verify the potion is a hardcore only ability of a live witch.
        Check both the normal mode and the dead witch.
        made by: Mohammad Abu Aresh
        """
        player = make_player(6, 5)
        self.witch.is_hardcore = False
        self.assertFalse(self.witch.throw_slow_potion(player))
        self.witch.is_hardcore = True
        self.witch.live = False
        self.assertFalse(self.witch.throw_slow_potion(player))
        self.assertEqual(self.witch.potions, [])

    def test_slow_expires_after_duration(self) -> None:
        """Verify the slow effect ends after its duration.
        Check the normal speed and the slowed flag return.
        made by: Mohammad Abu Aresh
        """
        player = make_player(6, 5)
        self.throw(player)
        land(self.witch, player)
        player.update_slow(4.9)
        self.assertAlmostEqual(player.speed, 0.035)
        player.update_slow(0.2)
        self.assertEqual(player.speed, 0.1)
        self.assertFalse(player.is_slowed)

    def test_repeated_potion_does_not_stack(self) -> None:
        """Verify two potions do not slow the player twice.
        Check the original speed returns after the effect ends.
        made by: Mohammad Abu Aresh
        """
        player = make_player(6, 5)
        SlowPotion((5, 5)).apply_effect(player)
        SlowPotion((5, 5)).apply_effect(player)
        self.assertAlmostEqual(player.speed, 0.035)
        player.update_slow(6.0)
        self.assertEqual(player.speed, 0.1)

    def test_cooldown_blocks_second_throw(self) -> None:
        """Verify the witch waits for the full cooldown.
        Check a new potion appears once the cooldown has ended.
        made by: Mohammad Abu Aresh
        """
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
        """Verify resetting the AI removes every potion in flight.
        Use it for a clean state after a player death.
        made by: Mohammad Abu Aresh
        """
        self.witch.throw_slow_potion(make_player(6, 5))
        self.witch.reset_ai()
        self.assertEqual(self.witch.potions, [])


class SlowClearTests(unittest.TestCase):
    def test_death_removes_the_slow_effect(self) -> None:
        """Verify respawning after a death removes the slow potion.
        Check the speed, the slowed flag and the lost life.
        made by: Mohammad Abu Aresh
        """
        player = make_player(6, 5)
        player._lives = 3
        player.spawn_point = (1, 1)
        SlowPotion((5, 5)).apply_effect(player)
        self.assertTrue(player.is_slowed)
        with patch.object(Player, "telport"):
            player.respawn()
        self.assertFalse(player.is_slowed)
        self.assertEqual(player.speed, 0.1)
        self.assertEqual(player._lives, 2)
        player.update_slow(10.0)
        self.assertEqual(player.speed, 0.1)

    def test_clearing_without_a_slow_keeps_the_speed(self) -> None:
        """Verify clearing a player that is not slowed changes nothing.
        Check the speed stays at its normal value.
        made by: Mohammad Abu Aresh
        """
        player = make_player(6, 5)
        player.clear_slow()
        self.assertEqual(player.speed, 0.1)
        self.assertFalse(player.is_slowed)

    def test_monster_reset_after_death_removes_flying_potions(self) -> None:
        """Verify the witch drops every potion in flight on a reset.
        A potion thrown before the death must not land afterwards.
        made by: Mohammad Abu Aresh
        """
        Block.size = 40
        witch = Witch((5, 5), True)
        player = make_player(6, 5)
        witch.throw_slow_potion(player)
        witch.reset_ai()
        witch.potion_timer = witch.potion_cooldown
        land(witch, player, 30)
        self.assertFalse(player.is_slowed)


if __name__ == "__main__":
    unittest.main()
