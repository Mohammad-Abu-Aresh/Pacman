import unittest

from ghost_ai_fixtures import MODES, FakeController


class GhostScheduleTests(unittest.TestCase):
    def test_level_schedules_match_arcade_timing_bands(self) -> None:
        """Verify the first, middle, and late-level timing bands.
        Check the long third Chase and final one-frame Scatter intervals.
        made by: Mohammad Abu Aresh
        """
        level_one = MODES.mode_schedule_for_level(1)
        level_three = MODES.mode_schedule_for_level(3)
        level_five = MODES.mode_schedule_for_level(5)
        self.assertEqual(level_one[5], ("chase", 20.0))
        self.assertEqual(level_three[5], ("chase", 1033.0))
        self.assertEqual(level_three[6], ("scatter", 1 / 60))
        self.assertEqual(level_five[0], ("scatter", 5.0))
        self.assertEqual(level_five[5], ("chase", 1037.0))

    def test_group_level_resets_each_monster_to_scatter(self) -> None:
        """Apply the selected mode schedule to all four monsters.
        Confirm each monster restarts at its new level's first phase.
        made by: Mohammad Abu Aresh
        """
        controller = FakeController()
        MODES.set_group_level(controller, 5)
        for monster in (
            controller.BabyZombie,
            controller.Skeleton,
            controller.Enderman,
            controller.witch,
        ):
            self.assertEqual(monster.MODE_SCHEDULE[0], ("scatter", 5.0))
            self.assertEqual(monster.reset_count, 1)


if __name__ == "__main__":
    unittest.main()
