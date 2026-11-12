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
        effects = ParticleEffects()
        effects.burst(3.0, 4.0, POTION_COLOR, 10)
        self.assertEqual(len(effects.particles), 10)
        self.assertTrue(all(p.x == 3.0 for p in effects.particles))

    def test_particles_expire(self) -> None:
        effects = ParticleEffects()
        effects.burst(1.0, 1.0, POTION_COLOR)
        effects.update(1.0)
        self.assertEqual(effects.particles, [])

    def test_particles_drift_while_alive(self) -> None:
        effects = ParticleEffects()
        effects.burst(1.0, 1.0, POTION_COLOR, 5)
        effects.update(0.1)
        self.assertEqual(len(effects.particles), 5)
        self.assertTrue(any(p.y != 1.0 for p in effects.particles))

    def test_trail_emits_on_interval_only(self) -> None:
        effects = ParticleEffects()
        effects.trail(1.0, 1.0, POTION_COLOR, 0.01)
        self.assertEqual(len(effects.particles), 1)
        effects.trail(1.0, 1.0, POTION_COLOR, 0.05)
        self.assertEqual(len(effects.particles), 1)
        effects.trail(1.0, 1.0, POTION_COLOR, 0.06)
        self.assertEqual(len(effects.particles), 2)

    def test_clear_removes_everything(self) -> None:
        effects = ParticleEffects()
        effects.burst(1.0, 1.0, POTION_COLOR)
        effects.clear()
        self.assertEqual(effects.particles, [])


class FlyTowardsTests(unittest.TestCase):
    def test_moves_straight_toward_goal(self) -> None:
        x, y, arrived = fly_towards((0.0, 0.0), (10.0, 0.0), 5.0, 1.0)
        self.assertEqual((x, y, arrived), (5.0, 0.0, False))

    def test_arrives_exactly_without_overshoot(self) -> None:
        x, y, arrived = fly_towards((0.0, 0.0), (3.0, 4.0), 100.0, 1.0)
        self.assertEqual((x, y, arrived), (3.0, 4.0, True))


class GroupAbilitiesWiringTests(unittest.TestCase):
    def controller(self, landed: bool, teleports: list[Any]) -> Any:
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
        controller = self.controller(True, [(5.0, 5.0)])
        update_group_abilities(controller, 0.01)
        self.assertEqual(len(controller.effects.particles), 14 + 14 + 1)

    def test_no_events_only_trail_while_slowed(self) -> None:
        controller = self.controller(False, [])
        update_group_abilities(controller, 0.01)
        self.assertEqual(len(controller.effects.particles), 1)

    def test_arrow_result_depends_on_super_state(self) -> None:
        controller = self.controller(False, [])
        self.assertTrue(update_group_abilities(controller, 0.01))
        controller.frightened_timer = 5.0
        self.assertFalse(update_group_abilities(controller, 0.01))


if __name__ == "__main__":
    unittest.main()
