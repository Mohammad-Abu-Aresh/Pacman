import os
import unittest
from types import SimpleNamespace
from typing import Any

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from game.block import Block  # noqa: E402
from game.creature.enderman import Enderman  # noqa: E402
from game.creature.player import Direction  # noqa: E402


def make_grid() -> list[list[bool]]:
    rows = ["#" * 14] + ["#" + "." * 12 + "#"] * 12 + ["#" * 14]
    grid = [[char == "#" for char in row] for row in rows]
    grid[6][6] = True
    return grid


def run(enderman: Enderman, player: Any, grid: list[list[bool]],
        seconds: float, frame: float = 0.5) -> list[tuple[float, float]]:
    bursts: list[tuple[float, float]] = []
    for _ in range(round(seconds / frame)):
        bursts += enderman.update_teleport(player, grid, frame)
    return bursts


class EndermanTeleportTests(unittest.TestCase):
    def setUp(self) -> None:
        Block.size = 40
        self.grid = make_grid()
        self.player: Any = SimpleNamespace(x=1.0, y=1.0)
        self.enderman = Enderman((10, 10), True)

    def test_cooldown_is_ten_seconds(self) -> None:
        self.assertEqual(self.enderman.teleport_cooldown, 10.0)

    def test_no_pearl_before_ten_seconds(self) -> None:
        run(self.enderman, self.player, self.grid, 9.5)
        self.assertIsNone(self.enderman.current_pearl)
        self.assertEqual((self.enderman.x, self.enderman.y), (10.0, 10.0))

    def test_throws_pearl_at_ten_seconds(self) -> None:
        bursts = run(self.enderman, self.player, self.grid, 10.0)
        self.assertIsNotNone(self.enderman.current_pearl)
        self.assertEqual(bursts, [(10.0, 10.0)])

    def test_lands_on_open_cell_far_from_player(self) -> None:
        for _ in range(20):
            enderman = Enderman((10, 10), True)
            run(enderman, self.player, self.grid, 10.0)
            pearl = enderman.current_pearl
            assert pearl is not None
            target = (pearl.target_x, pearl.target_y)
            bursts = run(enderman, self.player, self.grid, 5.0)
            self.assertIsNone(enderman.current_pearl)
            self.assertEqual((enderman.x, enderman.y), target)
            self.assertFalse(self.grid[target[1]][target[0]])
            self.assertGreaterEqual(
                abs(target[0] - 1) + abs(target[1] - 1), 4
            )
            self.assertEqual(bursts, [(float(target[0]), float(target[1]))])

    def test_repeats_every_ten_seconds(self) -> None:
        run(self.enderman, self.player, self.grid, 10.0)
        run(self.enderman, self.player, self.grid, 5.0)
        run(self.enderman, self.player, self.grid, 4.5)
        self.assertIsNone(self.enderman.current_pearl)
        run(self.enderman, self.player, self.grid, 1.0)
        self.assertIsNotNone(self.enderman.current_pearl)

    def test_waits_while_frightened_then_teleports_when_red(self) -> None:
        self.enderman.frightened = True
        run(self.enderman, self.player, self.grid, 12.0)
        self.assertIsNone(self.enderman.current_pearl)
        self.enderman.frightened = False
        run(self.enderman, self.player, self.grid, 0.5)
        self.assertIsNotNone(self.enderman.current_pearl)

    def test_inactive_without_hardcore(self) -> None:
        enderman = Enderman((10, 10), False)
        run(enderman, self.player, self.grid, 12.0)
        self.assertIsNone(enderman.current_pearl)

    def test_dead_enderman_does_not_teleport(self) -> None:
        self.enderman.live = False
        run(self.enderman, self.player, self.grid, 12.0)
        self.assertIsNone(self.enderman.current_pearl)

    def test_eaten_in_flight_does_not_teleport(self) -> None:
        run(self.enderman, self.player, self.grid, 10.0)
        self.enderman.live = False
        run(self.enderman, self.player, self.grid, 5.0)
        self.assertIsNone(self.enderman.current_pearl)
        self.assertEqual((self.enderman.x, self.enderman.y), (10.0, 10.0))

    def test_landing_resets_movement_state(self) -> None:
        self.enderman.next_point = (9, 10)
        self.enderman.movement_direction = Direction.left
        run(self.enderman, self.player, self.grid, 15.0)
        self.assertIsNone(self.enderman.next_point)
        self.assertEqual(self.enderman.movement_direction, Direction.none)

    def test_no_open_destination_means_no_pearl(self) -> None:
        grid = [[True] * 14 for _ in range(14)]
        grid[10][10] = False
        run(self.enderman, self.player, grid, 12.0)
        self.assertIsNone(self.enderman.current_pearl)

    def test_reset_clears_pearl_and_timer(self) -> None:
        run(self.enderman, self.player, self.grid, 10.0)
        self.enderman.reset_ai()
        self.assertIsNone(self.enderman.current_pearl)
        self.assertEqual(self.enderman.teleport_timer, 10.0)


if __name__ == "__main__":
    unittest.main()
