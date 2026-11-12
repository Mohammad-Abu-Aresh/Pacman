import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from game.block import Block  # noqa: E402
from game.creature.skeleton import Skeleton  # noqa: E402


def lane(length: int) -> list[list[bool]]:
    """Build a walled corridor with one open row.
    The spawn cell of the test monster is the first open cell.
    made by: Mohammad Abu Aresh
    """
    wall = [True] * (length + 2)
    row = [True] + [False] * length + [True]
    return [wall, row, wall]


def eaten_skeleton(start_x: int) -> Skeleton:
    """Create an eaten skeleton standing on the given column.
    Its spawn point is the first open cell of the corridor.
    made by: Mohammad Abu Aresh
    """
    skeleton = Skeleton((1, 1), True)
    skeleton.x = float(start_x)
    skeleton.y = 1.0
    skeleton.die()
    return skeleton


def seconds_until_revived(
    skeleton: Skeleton, grid: list[list[bool]], frame: float
) -> float:
    """Move a dead monster frame by frame until it is alive again.
    Return the simulated time that passed, with a ten second limit.
    made by: Mohammad Abu Aresh
    """
    elapsed = 0.0
    while not skeleton.live and elapsed < 10.0:
        skeleton.move(grid, frame, (1, 1))
        elapsed += frame
    return elapsed


class GhostRespawnTests(unittest.TestCase):
    def setUp(self) -> None:
        """Set the block size used by the monster constructors.
        Run it before every respawn test.
        made by: Mohammad Abu Aresh
        """
        Block.size = 40

    def test_near_and_far_monsters_revive_after_three_seconds(self) -> None:
        """Verify the revive time does not depend on the distance.
        Check a close and a far monster with exact binary frames.
        made by: Mohammad Abu Aresh
        """
        grid = lane(30)
        for start_x in (3, 12, 30):
            skeleton = eaten_skeleton(start_x)
            self.assertEqual(seconds_until_revived(skeleton, grid, 0.25), 3.0)

    def test_monster_is_still_dead_just_before_three_seconds(self) -> None:
        """Verify the monster stays dead until the time has ended.
        Check it after eleven quarter second frames.
        made by: Mohammad Abu Aresh
        """
        grid = lane(30)
        skeleton = eaten_skeleton(20)
        for _ in range(11):
            skeleton.move(grid, 0.25, (1, 1))
        self.assertFalse(skeleton.live)

    def test_revive_time_with_sixty_frames_per_second(self) -> None:
        """Verify the revive time is three seconds at a normal frame rate.
        Allow one frame of difference from the float accumulation.
        made by: Mohammad Abu Aresh
        """
        grid = lane(30)
        for start_x in (2, 15, 30):
            skeleton = eaten_skeleton(start_x)
            elapsed = seconds_until_revived(skeleton, grid, 1 / 60)
            self.assertGreaterEqual(elapsed, 3.0 - 1e-9)
            self.assertLess(elapsed, 3.0 + 1 / 60 + 1e-9)

    def test_return_speed_depends_on_the_distance(self) -> None:
        """Verify a farther monster returns with a higher speed.
        Check the speed equals the path length divided by three.
        made by: Mohammad Abu Aresh
        """
        grid = lane(30)
        near = eaten_skeleton(4)
        far = eaten_skeleton(25)
        near.move(grid, 0.0, (1, 1))
        far.move(grid, 0.0, (1, 1))
        self.assertAlmostEqual(near.return_speed, 3 / 3.0)
        self.assertAlmostEqual(far.return_speed, 24 / 3.0)
        self.assertGreater(far.return_speed, near.return_speed)

    def test_monster_revives_on_its_spawn_cell(self) -> None:
        """Verify the revived monster stands on its spawn point.
        Check the live flag and the exact coordinates.
        made by: Mohammad Abu Aresh
        """
        grid = lane(30)
        skeleton = eaten_skeleton(20)
        seconds_until_revived(skeleton, grid, 0.25)
        self.assertTrue(skeleton.live)
        self.assertEqual((skeleton.x, skeleton.y), (1.0, 1.0))

    def test_monster_dead_on_its_spawn_still_waits(self) -> None:
        """Verify a monster eaten on its spawn also waits three seconds.
        Check both the waiting and the final revive time.
        made by: Mohammad Abu Aresh
        """
        grid = lane(30)
        skeleton = eaten_skeleton(1)
        skeleton.move(grid, 1.0, (1, 1))
        self.assertFalse(skeleton.live)
        self.assertEqual(seconds_until_revived(skeleton, grid, 1.0), 2.0)

    def test_monster_travels_toward_spawn_while_dead(self) -> None:
        """Verify the dead monster keeps moving toward its spawn.
        Check its position after one and a half seconds.
        made by: Mohammad Abu Aresh
        """
        grid = lane(30)
        skeleton = eaten_skeleton(25)
        for _ in range(90):
            skeleton.move(grid, 1 / 60, (1, 1))
        self.assertLess(skeleton.x, 25.0)
        self.assertGreater(skeleton.x, 1.0)

    def test_early_arrival_does_not_revive_early(self) -> None:
        """Verify reaching the spawn early does not revive the monster.
        Force a very high speed and check it still waits.
        made by: Mohammad Abu Aresh
        """
        grid = lane(30)
        skeleton = eaten_skeleton(10)
        skeleton.move(grid, 0.05, (1, 1))
        skeleton.return_speed = 1000.0
        for _ in range(20):
            skeleton.move(grid, 0.05, (1, 1))
        self.assertFalse(skeleton.live)
        self.assertEqual(skeleton.x, 1.0)


if __name__ == "__main__":
    unittest.main()
