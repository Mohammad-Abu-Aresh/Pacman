import unittest
from unittest.mock import patch

from ghost_ai_fixtures import LIFECYCLE, FakeController


class GhostLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        """Create fresh test doubles for each lifecycle scenario.
        Replace sprite rendering so tests do not require a display device.
        made by: Mohammad Abu Aresh
        """
        self.controller = FakeController()
        self.monster = self.controller.BabyZombie
        self.visual_patch = patch.object(
            LIFECYCLE, "set_monster_eaten_visual", lambda monster: None
        )
        self.visual_patch.start()
        self.addCleanup(self.visual_patch.stop)

    def test_monster_can_be_eaten_only_once_per_pellet(self) -> None:
        """Allow one eat in a cycle and restore danger at the spawn.
        Start a later cycle to grant the monster a fresh eating opportunity.
        made by: Mohammad Abu Aresh
        """
        LIFECYCLE.start_power_pellet_cycle(self.controller, 15.0)
        self.assertTrue(LIFECYCLE.mark_monster_eaten(
            self.controller, self.monster, 200
        ))
        self.assertFalse(self.monster.live)
        self.assertFalse(LIFECYCLE.mark_monster_eaten(
            self.controller, self.monster, 200
        ))
        self.assertEqual(self.controller.player.score, 200)

        self.assertTrue(LIFECYCLE.reactivate_eaten_monster(self.monster))
        self.assertTrue(self.monster.live)
        self.assertFalse(self.monster.frightened)
        self.assertEqual(self.monster.image, "normal")

        LIFECYCLE.start_power_pellet_cycle(self.controller, 15.0)
        self.assertTrue(self.monster.frightened)
        self.assertTrue(LIFECYCLE.mark_monster_eaten(
            self.controller, self.monster, 200
        ))
        self.assertEqual(self.controller.player.score, 400)

    def test_eaten_monster_finishes_its_current_tile_step(self) -> None:
        """Preserve a valid in-progress step when the monster is eaten.
        Let it reach the next tile center before BFS selects its return route.
        made by: Mohammad Abu Aresh
        """
        LIFECYCLE.start_power_pellet_cycle(self.controller, 15.0)
        self.monster.next_point = (2, 1)
        self.assertTrue(LIFECYCLE.mark_monster_eaten(
            self.controller, self.monster, 200
        ))
        self.assertFalse(self.monster.live)
        self.assertEqual(self.monster.target_point, self.monster.spawn_point)
        self.assertEqual(self.monster.next_point, (2, 1))

    def test_returning_monster_joins_a_new_active_pellet_cycle(self) -> None:
        """Carry a new Power Pellet state into a monster already returning.
        Reactivate it frightened only while that newer cycle remains active.
        made by: Mohammad Abu Aresh
        """
        LIFECYCLE.start_power_pellet_cycle(self.controller, 15.0)
        LIFECYCLE.mark_monster_eaten(self.controller, self.monster, 200)
        LIFECYCLE.start_power_pellet_cycle(self.controller, 12.0)
        self.controller.frightened_timer = 8.0
        LIFECYCLE.sync_returning_monsters(self.controller)

        self.assertTrue(LIFECYCLE.reactivate_eaten_monster(self.monster))
        self.assertTrue(self.monster.live)
        self.assertTrue(self.monster.frightened)
        self.assertEqual(self.monster.frightened_timer, 8.0)

    def test_expired_pending_cycle_reactivates_as_dangerous(self) -> None:
        """Discard pending frightened state after the group timer expires.
        Ensure the returning monster restores its normal image and danger.
        made by: Mohammad Abu Aresh
        """
        LIFECYCLE.start_power_pellet_cycle(self.controller, 15.0)
        LIFECYCLE.mark_monster_eaten(self.controller, self.monster, 200)
        LIFECYCLE.start_power_pellet_cycle(self.controller, 12.0)
        self.controller.frightened_timer = 0.0
        LIFECYCLE.sync_returning_monsters(self.controller)

        self.assertTrue(LIFECYCLE.reactivate_eaten_monster(self.monster))
        self.assertTrue(self.monster.live)
        self.assertFalse(self.monster.frightened)
        self.assertEqual(self.monster.image, "normal")

    def test_group_mode_clock_pauses_and_resumes(self) -> None:
        """Pause ghost mode clocks while frightened and resume afterward.
        Verify group state remains synchronized for all four monsters.
        made by: Mohammad Abu Aresh
        """
        LIFECYCLE.start_power_pellet_cycle(self.controller, 5.0)
        monsters = (
            self.controller.BabyZombie,
            self.controller.Skeleton,
            self.controller.Enderman,
            self.controller.witch,
        )
        self.assertTrue(all(m.lifecycle.mode_clock_paused for m in monsters))
        self.controller.frightened_timer = 0.0
        LIFECYCLE.sync_returning_monsters(self.controller)
        self.assertTrue(
            all(not m.lifecycle.mode_clock_paused for m in monsters)
        )


if __name__ == "__main__":
    unittest.main()
