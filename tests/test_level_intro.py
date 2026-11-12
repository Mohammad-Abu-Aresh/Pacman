import os
import unittest
from types import SimpleNamespace
from typing import Any

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from game.creature.effects import ParticleEffects  # noqa: E402
from game.level_intro import LevelIntro, announce_spawns  # noqa: E402


def intro_at(seconds: float) -> LevelIntro:
    """Create an intro whose clock already shows the given time.
    Use one single update so the test reads like a timeline.
    made by: Mohammad Abu Aresh
    """
    intro = LevelIntro()
    intro.update(seconds)
    return intro


class LevelIntroTimelineTests(unittest.TestCase):
    def test_maze_is_hidden_for_the_first_three_seconds(self) -> None:
        """Verify the maze is not visible before three seconds.
        Check the start of the level and the last hidden moment.
        made by: Mohammad Abu Aresh
        """
        self.assertEqual(intro_at(0.0).maze_progress(), 0.0)
        self.assertEqual(intro_at(2.99).maze_progress(), 0.0)

    def test_maze_is_revealed_after_the_hidden_time(self) -> None:
        """Verify the maze reveal grows from three to four seconds.
        Check the middle and the end of the reveal.
        made by: Mohammad Abu Aresh
        """
        self.assertAlmostEqual(intro_at(3.5).maze_progress(), 0.5)
        self.assertEqual(intro_at(4.0).maze_progress(), 1.0)
        self.assertEqual(intro_at(30.0).maze_progress(), 1.0)

    def test_nothing_spawns_before_the_maze_is_revealed(self) -> None:
        """Verify no creature and no gum exists while revealing.
        Check just before the spawn phase begins.
        made by: Mohammad Abu Aresh
        """
        intro = intro_at(3.99)
        self.assertEqual(intro.visible_actor_count(5), 0)
        self.assertEqual(intro.visible_collectible_count(100), 0)

    def test_player_spawns_first_then_monsters_one_by_one(self) -> None:
        """Verify creatures appear in order with a short gap.
        Check the count at several moments of the spawn phase.
        made by: Mohammad Abu Aresh
        """
        self.assertEqual(intro_at(4.0).visible_actor_count(5), 1)
        self.assertEqual(intro_at(4.3).visible_actor_count(5), 2)
        self.assertEqual(intro_at(4.55).visible_actor_count(5), 3)
        self.assertEqual(intro_at(5.0).visible_actor_count(5), 5)

    def test_gums_fill_the_maze_in_steps(self) -> None:
        """Verify gums are revealed gradually and then all at once.
        Check that the count never decreases during the phase.
        made by: Mohammad Abu Aresh
        """
        counts = [
            intro_at(4.0 + step * 0.1).visible_collectible_count(200)
            for step in range(16)
        ]
        self.assertEqual(counts, sorted(counts))
        self.assertGreater(counts[7], 0)
        self.assertLess(counts[3], 200)
        self.assertEqual(counts[-1], 200)

    def test_everything_has_spawned_before_the_countdown(self) -> None:
        """Verify the countdown starts after all spawns finished.
        Check creatures and gums at the first countdown moment.
        made by: Mohammad Abu Aresh
        """
        intro = intro_at(5.5)
        self.assertEqual(intro.visible_actor_count(5), 5)
        self.assertEqual(intro.visible_collectible_count(200), 200)
        self.assertIsNone(intro_at(5.49).countdown_number())

    def test_countdown_shows_three_two_one(self) -> None:
        """Verify the countdown numbers and their one second pace.
        Check that nothing is shown after the last number.
        made by: Mohammad Abu Aresh
        """
        self.assertEqual(intro_at(5.5).countdown_number(), 3)
        self.assertEqual(intro_at(6.5).countdown_number(), 2)
        self.assertEqual(intro_at(7.5).countdown_number(), 1)
        self.assertIsNone(intro_at(8.5).countdown_number())

    def test_countdown_fraction_stays_inside_one_second(self) -> None:
        """Verify the animation fraction is between zero and one.
        Check the start and the middle of a number.
        made by: Mohammad Abu Aresh
        """
        self.assertEqual(intro_at(5.5).countdown_fraction(), 0.0)
        self.assertAlmostEqual(intro_at(6.0).countdown_fraction(), 0.5)

    def test_gameplay_is_frozen_until_the_countdown_ends(self) -> None:
        """Verify the update blocks the gameplay for eight and a half seconds.
        Check the last frozen frame and the first free frame.
        made by: Mohammad Abu Aresh
        """
        intro = LevelIntro()
        self.assertTrue(intro.update(8.49))
        self.assertFalse(intro.update(0.02))
        self.assertFalse(intro.update(1.0))

    def test_restart_hides_the_maze_again(self) -> None:
        """Verify a restart brings back the hidden maze phase.
        Check the progress and the announced creature counter.
        made by: Mohammad Abu Aresh
        """
        intro = intro_at(9.0)
        intro.announced = 5
        intro.restart()
        self.assertEqual(intro.maze_progress(), 0.0)
        self.assertEqual(intro.announced, 0)
        self.assertTrue(intro.active)

    def test_story_is_typed_live_at_a_fixed_speed(self) -> None:
        """Verify the story grows over time and never exceeds its length.
        Check the start, one second and a very late moment.
        made by: Mohammad Abu Aresh
        """
        self.assertEqual(intro_at(0.0).story_chars(140), 0)
        self.assertEqual(intro_at(1.0).story_chars(140), 30)
        self.assertEqual(intro_at(60.0).story_chars(140), 140)


class SpawnAnnouncementTests(unittest.TestCase):
    def game(self, intro: LevelIntro) -> Any:
        """Build a light game with five creatures and a particle list.
        The creatures only carry their grid coordinates.
        made by: Mohammad Abu Aresh
        """
        mobs = tuple(SimpleNamespace(x=float(i), y=1.0) for i in range(5))
        return SimpleNamespace(
            intro=intro,
            mobs=mobs,
            player_creature=SimpleNamespace(effects=ParticleEffects()),
        )

    def test_each_spawn_bursts_once(self) -> None:
        """Verify particles appear once for every spawned creature.
        Check that repeated frames do not repeat the burst.
        made by: Mohammad Abu Aresh
        """
        intro = LevelIntro()
        game = self.game(intro)
        intro.update(4.0)
        announce_spawns(game, 0.0)
        announce_spawns(game, 0.0)
        self.assertEqual(len(game.player_creature.effects.particles), 14)
        intro.update(1.0)
        announce_spawns(game, 0.0)
        self.assertEqual(len(game.player_creature.effects.particles), 70)
        self.assertEqual(intro.announced, 5)


if __name__ == "__main__":
    unittest.main()
