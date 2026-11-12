import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from game.creature.abilities import fly_towards  # noqa: E402
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


if __name__ == "__main__":
    unittest.main()
