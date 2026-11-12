import os
import unittest
from types import SimpleNamespace
from typing import Any

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from game.creature.abilities import fly_towards  # noqa: E402
from game.creature.ability_state import (  # noqa: E402
    update_group_abilities,
)
from game.creature.effects import (  # noqa: E402
    POTION_COLOR,
    ParticleEffects,
)


class ParticleEffectsTests(unittest.TestCase):
    def test_burst_creates_requested_particles(self) -> None:
        """Verify a burst creates the requested number of particles.
        Check they all start at the burst position.
        made by: Mohammad Abu Aresh
        """
        effects = ParticleEffects()
        effects.burst(3.0, 4.0, POTION_COLOR, 10)
        self.assertEqual(len(effects.particles), 10)
        self.assertTrue(all(p.x == 3.0 for p in effects.particles))

    def test_particles_expire(self) -> None:
        """Verify particles are removed after their lifetime.
        A long update must leave the list empty.
        made by: Mohammad Abu Aresh
        """
        effects = ParticleEffects()
        effects.burst(1.0, 1.0, POTION_COLOR)
        effects.update(1.0)
        self.assertEqual(effects.particles, [])

    def test_particles_drift_while_alive(self) -> None:
        """Verify particles keep moving while they are alive.
        A short update must not remove any particle.
        made by: Mohammad Abu Aresh
        """
        effects = ParticleEffects()
        effects.burst(1.0, 1.0, POTION_COLOR, 5)
        effects.update(0.1)
        self.assertEqual(len(effects.particles), 5)
        self.assertTrue(any(p.y != 1.0 for p in effects.particles))

    def test_trail_emits_on_interval_only(self) -> None:
        """Verify the trail emits one particle per interval.
        Short updates in between must emit nothing.
        made by: Mohammad Abu Aresh
        """
        effects = ParticleEffects()
        effects.trail(1.0, 1.0, POTION_COLOR, 0.01)
        self.assertEqual(len(effects.particles), 1)
        effects.trail(1.0, 1.0, POTION_COLOR, 0.05)
        self.assertEqual(len(effects.particles), 1)
        effects.trail(1.0, 1.0, POTION_COLOR, 0.06)
        self.assertEqual(len(effects.particles), 2)

    def test_clear_removes_everything(self) -> None:
        """Verify clearing removes every particle.
        Use it for a clean state after a reset.
        made by: Mohammad Abu Aresh
        """
        effects = ParticleEffects()
        effects.burst(1.0, 1.0, POTION_COLOR)
        effects.clear()
        self.assertEqual(effects.particles, [])


class FlyTowardsTests(unittest.TestCase):
    def test_moves_straight_toward_goal(self) -> None:
        """Verify one step moves along a straight line to the goal.
        Check the position and that the goal is not reached yet.
        made by: Mohammad Abu Aresh
        """
        x, y, arrived = fly_towards((0.0, 0.0), (10.0, 0.0), 5.0, 1.0)
        self.assertEqual((x, y, arrived), (5.0, 0.0, False))

    def test_arrives_exactly_without_overshoot(self) -> None:
        """Verify a large step lands exactly on the goal.
        Check the arrived flag is set.
        made by: Mohammad Abu Aresh
        """
        x, y, arrived = fly_towards((0.0, 0.0), (3.0, 4.0), 100.0, 1.0)
        self.assertEqual((x, y, arrived), (3.0, 4.0, True))


class GroupAbilitiesWiringTests(unittest.TestCase):
    def controller(self, landed: bool, teleports: list[Any]) -> Any:
        """Build a light controller with stand in monsters.
        Each stand in returns the values chosen by the test.
        made by: Mohammad Abu Aresh
        """
        return SimpleNamespace(
            player=SimpleNamespace(
                x=2.0, y=2.0, is_slowed=True, update_slow=lambda dt: None
            ),
            BabyZombie=SimpleNamespace(sync_hardcore_speed=lambda: None),
            witch=SimpleNamespace(update_potion=lambda p, dt: landed),
            Enderman=SimpleNamespace(
                update_teleport=lambda p, grid, dt: teleports
            ),
            Skeleton=SimpleNamespace(
                update_arrows=lambda p, m, dt, hurt: hurt
            ),
            maze_mape=SimpleNamespace(every_cell=[[False]]),
            effects=ParticleEffects(),
            frightened_timer=0.0,
        )

    def test_potion_landing_and_teleport_spawn_particles(self) -> None:
        """Verify a landed potion and a teleport create bursts.
        Check the slow trail adds one more particle.
        made by: Mohammad Abu Aresh
        """
        controller = self.controller(True, [(5.0, 5.0)])
        update_group_abilities(controller, 0.01)
        self.assertEqual(len(controller.effects.particles), 14 + 14 + 1)

    def test_no_events_only_trail_while_slowed(self) -> None:
        """Verify only the slow trail appears when nothing lands.
        Check exactly one particle is created.
        made by: Mohammad Abu Aresh
        """
        controller = self.controller(False, [])
        update_group_abilities(controller, 0.01)
        self.assertEqual(len(controller.effects.particles), 1)

    def test_arrow_result_depends_on_super_state(self) -> None:
        """Verify arrows can hurt only while the player is not super.
        Check the returned value follows the frightened timer.
        made by: Mohammad Abu Aresh
        """
        controller = self.controller(False, [])
        self.assertTrue(update_group_abilities(controller, 0.01))
        controller.frightened_timer = 5.0
        self.assertFalse(update_group_abilities(controller, 0.01))


if __name__ == "__main__":
    unittest.main()
