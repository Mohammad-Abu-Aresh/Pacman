import os
import unittest
from collections.abc import Callable
from types import SimpleNamespace
from typing import Any

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from game.block import Block  # noqa: E402
from game.creature.abilities import Arrow  # noqa: E402
from game.creature.player import Direction  # noqa: E402
from game.creature.skeleton import Skeleton  # noqa: E402


def make_grid(rows: list[str]) -> list[list[bool]]:
    return [[char == "#" for char in row] for row in rows]


def fly(arrow: Arrow, grid: list[list[bool]], seconds: float,
        frame: float) -> None:
    for _ in range(round(seconds / frame)):
        arrow.move(grid, frame)


class ArrowMovementTests(unittest.TestCase):
    def setUp(self) -> None:
        Block.size = 40
        self.grid = make_grid(["#########"] * 1 + ["#.......#"] * 7
                              + ["#########"])

    def test_moves_right(self) -> None:
        arrow = Arrow((2, 4), Direction.right)
        arrow.move(self.grid, 0.1)
        self.assertAlmostEqual(arrow.x, 3.5)
        self.assertEqual(arrow.y, 4.0)

    def test_moves_left(self) -> None:
        arrow = Arrow((6, 4), Direction.left)
        arrow.move(self.grid, 0.1)
        self.assertAlmostEqual(arrow.x, 4.5)
        self.assertEqual(arrow.y, 4.0)

    def test_moves_up(self) -> None:
        arrow = Arrow((4, 6), Direction.up)
        arrow.move(self.grid, 0.1)
        self.assertAlmostEqual(arrow.y, 4.5)
        self.assertEqual(arrow.x, 4.0)

    def test_moves_down(self) -> None:
        arrow = Arrow((4, 2), Direction.down)
        arrow.move(self.grid, 0.1)
        self.assertAlmostEqual(arrow.y, 3.5)
        self.assertEqual(arrow.x, 4.0)

    def test_never_moves_diagonally(self) -> None:
        for direction in (Direction.right, Direction.left,
                          Direction.up, Direction.down):
            arrow = Arrow((4.4, 3.6), direction)
            start = (arrow.x, arrow.y)
            fly(arrow, self.grid, 1.0, 1 / 60)
            moved_x = arrow.x != start[0]
            moved_y = arrow.y != start[1]
            self.assertNotEqual(moved_x, moved_y)
            self.assertEqual(arrow.direction, direction)

    def test_does_not_expire_over_time(self) -> None:
        grid = make_grid(["#" * 202, "#" + "." * 200 + "#", "#" * 202])
        arrow = Arrow((1, 1), Direction.right)
        fly(arrow, grid, 5.0, 1 / 60)
        self.assertTrue(arrow.active)
        self.assertGreater(arrow.x, 70)

    def test_stops_at_wall(self) -> None:
        arrow = Arrow((2, 4), Direction.right)
        fly(arrow, self.grid, 1.0, 1 / 60)
        self.assertFalse(arrow.active)
        self.assertLess(arrow.x, 8 - 0.5)

    def test_never_enters_wall_in_any_direction(self) -> None:
        cases: dict[
            tuple[int, int],
            tuple[tuple[int, int], Callable[[Arrow], bool]],
        ] = {
            Direction.right: ((2, 4), lambda a: a.x < 7.5),
            Direction.left: ((6, 4), lambda a: a.x >= 0.5),
            Direction.up: ((4, 6), lambda a: a.y >= 0.5),
            Direction.down: ((4, 2), lambda a: a.y < 7.5),
        }
        for direction, (spawn, inside) in cases.items():
            arrow = Arrow(spawn, direction)
            fly(arrow, self.grid, 1.0, 1 / 60)
            self.assertFalse(arrow.active)
            self.assertTrue(inside(arrow), direction)
            x, y = arrow.cell()
            self.assertFalse(self.grid[y][x])

    def test_large_delta_time_does_not_tunnel(self) -> None:
        grid = make_grid(["#######", "#..#..#", "#######"])
        arrow = Arrow((1, 1), Direction.right)
        arrow.move(grid, 10.0)
        self.assertFalse(arrow.active)
        self.assertLess(arrow.x, 2.5)

    def test_high_speed_does_not_tunnel(self) -> None:
        grid = make_grid(["#######", "#..#..#", "#######"])
        arrow = Arrow((1, 1), Direction.right, speed=100000)
        arrow.move(grid, 1 / 60)
        self.assertFalse(arrow.active)
        self.assertLess(arrow.x, 2.5)

    def test_grid_edge_is_safe(self) -> None:
        grid = make_grid(["...", "...", "..."])
        for direction, spawn in ((Direction.right, (1, 1)),
                                 (Direction.left, (1, 1)),
                                 (Direction.up, (1, 1)),
                                 (Direction.down, (1, 1))):
            arrow = Arrow(spawn, direction)
            arrow.move(grid, 5.0)
            self.assertFalse(arrow.active)
            x, y = arrow.cell()
            self.assertTrue(0 <= x < 3 and 0 <= y < 3)

    def test_sweep_includes_every_crossed_cell(self) -> None:
        arrow = Arrow((1, 4), Direction.right)
        arrow.move(self.grid, 0.2)
        self.assertEqual(arrow.swept_cells[0], (1, 4))
        self.assertEqual(arrow.swept_cells[-1], (4, 4))
        self.assertEqual(len(arrow.swept_cells), 4)


class SkeletonShootingTests(unittest.TestCase):
    def setUp(self) -> None:
        Block.size = 40
        self.mape: Any = SimpleNamespace(
            every_cell=make_grid(["#" * 42, "#" + "." * 40 + "#", "#" * 42])
        )
        self.skeleton = Skeleton((1, 1), True)

    def player(self, x: float, y: float) -> Any:
        return SimpleNamespace(x=x, y=y)

    def test_shoots_at_far_player_without_wall(self) -> None:
        self.skeleton.shoot_arrow(self.player(40, 1), self.mape)
        self.assertEqual(len(self.skeleton.active_arrows), 1)
        self.assertEqual(
            self.skeleton.active_arrows[0].direction, Direction.right
        )

    def test_does_not_shoot_through_wall(self) -> None:
        self.mape.every_cell[1][20] = True
        self.skeleton.shoot_arrow(self.player(40, 1), self.mape)
        self.assertEqual(self.skeleton.active_arrows, [])

    def test_does_not_shoot_when_not_hardcore(self) -> None:
        self.skeleton.is_hardcore = False
        self.skeleton.shoot_arrow(self.player(5, 1), self.mape)
        self.assertEqual(self.skeleton.active_arrows, [])

    def test_hit_is_reported_once_and_arrow_survives(self) -> None:
        self.skeleton.shoot_arrow(self.player(10, 1), self.mape)
        player = self.player(10, 1)
        hits = [
            self.skeleton.update_arrows(player, self.mape, 1 / 60)
            for _ in range(60)
        ]
        self.assertEqual(hits.count(True), 1)
        self.assertEqual(len(self.skeleton.active_arrows), 1)
        self.assertTrue(self.skeleton.active_arrows[0].hit_player)

    def test_arrow_removed_only_after_wall(self) -> None:
        self.skeleton.shoot_arrow(self.player(10, 1), self.mape)
        player = self.player(10, 1)
        for _ in range(240):
            self.skeleton.update_arrows(player, self.mape, 1 / 60)
        self.assertTrue(all(a.active for a in self.skeleton.active_arrows))
        for _ in range(60):
            self.skeleton.update_arrows(player, self.mape, 1 / 60)
        self.assertLessEqual(len(self.skeleton.active_arrows), 1)

    def test_cooldown_and_single_arrow_limit(self) -> None:
        player = self.player(5, 1)
        peak = 0
        for _ in range(60 * 10):
            self.skeleton.update_arrows(player, self.mape, 1 / 60)
            peak = max(peak, len(self.skeleton.active_arrows))
        self.assertEqual(peak, 1)
        self.skeleton.active_arrows.clear()
        self.skeleton.shoot_timer = 3.0
        self.skeleton.shoot_arrow(player, self.mape)
        self.assertEqual(self.skeleton.active_arrows, [])

    def test_reset_clears_arrows(self) -> None:
        self.skeleton.shoot_arrow(self.player(10, 1), self.mape)
        self.skeleton.reset_ai()
        self.assertEqual(self.skeleton.active_arrows, [])
        self.assertEqual(self.skeleton.shoot_timer, 0.0)


if __name__ == "__main__":
    unittest.main()
