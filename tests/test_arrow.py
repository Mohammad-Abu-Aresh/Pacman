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
    """Build a boolean wall grid from rows of text.
    A hash character marks a wall and a dot an open cell.
    made by: Mohammad Abu Aresh
    """
    return [[char == "#" for char in row] for row in rows]


def fly(arrow: Arrow, grid: list[list[bool]], seconds: float,
        frame: float) -> None:
    """Move an arrow for a number of fixed frames.
    Use the same grid and frame time on every step.
    made by: Mohammad Abu Aresh
    """
    for _ in range(round(seconds / frame)):
        arrow.move(grid, frame)


class ArrowMovementTests(unittest.TestCase):
    def setUp(self) -> None:
        """Prepare an enclosed room and a fixed block size.
        Every movement test starts from this same grid.
        made by: Mohammad Abu Aresh
        """
        Block.size = 40
        self.grid = make_grid(["#########"] * 1 + ["#.......#"] * 7
                              + ["#########"])

    def test_moves_right(self) -> None:
        """Verify an arrow moves horizontally to the right.
        Check that only the x coordinate changes.
        made by: Mohammad Abu Aresh
        """
        arrow = Arrow((2, 4), Direction.right)
        arrow.move(self.grid, 0.1)
        self.assertAlmostEqual(arrow.x, 3.5)
        self.assertEqual(arrow.y, 4.0)

    def test_moves_left(self) -> None:
        """Verify an arrow moves horizontally to the left.
        Check that only the x coordinate changes.
        made by: Mohammad Abu Aresh
        """
        arrow = Arrow((6, 4), Direction.left)
        arrow.move(self.grid, 0.1)
        self.assertAlmostEqual(arrow.x, 4.5)
        self.assertEqual(arrow.y, 4.0)

    def test_moves_up(self) -> None:
        """Verify an arrow moves vertically upward.
        Check that only the y coordinate changes.
        made by: Mohammad Abu Aresh
        """
        arrow = Arrow((4, 6), Direction.up)
        arrow.move(self.grid, 0.1)
        self.assertAlmostEqual(arrow.y, 4.5)
        self.assertEqual(arrow.x, 4.0)

    def test_moves_down(self) -> None:
        """Verify an arrow moves vertically downward.
        Check that only the y coordinate changes.
        made by: Mohammad Abu Aresh
        """
        arrow = Arrow((4, 2), Direction.down)
        arrow.move(self.grid, 0.1)
        self.assertAlmostEqual(arrow.y, 3.5)
        self.assertEqual(arrow.x, 4.0)

    def test_never_moves_diagonally(self) -> None:
        """Verify no direction ever changes both axes together.
        Also check the direction stays the same during the flight.
        made by: Mohammad Abu Aresh
        """
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
        """Verify a long flight in an open corridor never removes the arrow.
        Time alone must not deactivate it.
        made by: Mohammad Abu Aresh
        """
        grid = make_grid(["#" * 202, "#" + "." * 200 + "#", "#" * 202])
        arrow = Arrow((1, 1), Direction.right)
        fly(arrow, grid, 5.0, 1 / 60)
        self.assertTrue(arrow.active)
        self.assertGreater(arrow.x, 70)

    def test_stops_at_wall(self) -> None:
        """Verify the arrow is deactivated when it reaches a wall.
        Check it stops before the wall cell.
        made by: Mohammad Abu Aresh
        """
        arrow = Arrow((2, 4), Direction.right)
        fly(arrow, self.grid, 1.0, 1 / 60)
        self.assertFalse(arrow.active)
        self.assertLess(arrow.x, 8 - 0.5)

    def test_never_enters_wall_in_any_direction(self) -> None:
        """Verify the four directions never end inside a wall cell.
        Check the final cell is open for each direction.
        made by: Mohammad Abu Aresh
        """
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
        """Verify a huge frame time cannot jump over a wall.
        The arrow must stop before the first wall cell.
        made by: Mohammad Abu Aresh
        """
        grid = make_grid(["#######", "#..#..#", "#######"])
        arrow = Arrow((1, 1), Direction.right)
        arrow.move(grid, 10.0)
        self.assertFalse(arrow.active)
        self.assertLess(arrow.x, 2.5)

    def test_high_speed_does_not_tunnel(self) -> None:
        """Verify a very high speed cannot jump over a wall.
        The sweep must visit every crossed cell.
        made by: Mohammad Abu Aresh
        """
        grid = make_grid(["#######", "#..#..#", "#######"])
        arrow = Arrow((1, 1), Direction.right, speed=100000)
        arrow.move(grid, 1 / 60)
        self.assertFalse(arrow.active)
        self.assertLess(arrow.x, 2.5)

    def test_grid_edge_is_safe(self) -> None:
        """Verify flying out of the grid raises no index error.
        The arrow must stop on an in-bounds cell.
        made by: Mohammad Abu Aresh
        """
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
        """Verify the swept cells list every cell crossed in one frame.
        Check the first and last cells and the total count.
        made by: Mohammad Abu Aresh
        """
        arrow = Arrow((1, 4), Direction.right)
        arrow.move(self.grid, 0.2)
        self.assertEqual(arrow.swept_cells[0], (1, 4))
        self.assertEqual(arrow.swept_cells[-1], (4, 4))
        self.assertEqual(len(arrow.swept_cells), 4)


class SkeletonShootingTests(unittest.TestCase):
    def setUp(self) -> None:
        """Prepare a long open lane and a hardcore skeleton.
        The lane lets the player stand far away without any wall.
        made by: Mohammad Abu Aresh
        """
        Block.size = 40
        self.mape: Any = SimpleNamespace(
            every_cell=make_grid(["#" * 42, "#" + "." * 40 + "#", "#" * 42])
        )
        self.skeleton = Skeleton((1, 1), True)

    def player(self, x: float, y: float) -> Any:
        """Create a light player stand in with x and y coordinates.
        Only the position is needed by the shooting logic.
        made by: Mohammad Abu Aresh
        """
        return SimpleNamespace(x=x, y=y)

    def test_shoots_at_far_player_without_wall(self) -> None:
        """Verify the skeleton shoots at a distant player.
        Check there is one arrow aimed to the right.
        made by: Mohammad Abu Aresh
        """
        self.skeleton.shoot_arrow(self.player(40, 1), self.mape)
        self.assertEqual(len(self.skeleton.active_arrows), 1)
        self.assertEqual(
            self.skeleton.active_arrows[0].direction, Direction.right
        )

    def test_does_not_shoot_through_wall(self) -> None:
        """Verify a wall between both blocks the shot.
        No arrow may be created.
        made by: Mohammad Abu Aresh
        """
        self.mape.every_cell[1][20] = True
        self.skeleton.shoot_arrow(self.player(40, 1), self.mape)
        self.assertEqual(self.skeleton.active_arrows, [])

    def test_does_not_shoot_when_not_hardcore(self) -> None:
        """Verify a normal mode skeleton never shoots.
        Only the hardcore mode enables the arrow ability.
        made by: Mohammad Abu Aresh
        """
        self.skeleton.is_hardcore = False
        self.skeleton.shoot_arrow(self.player(5, 1), self.mape)
        self.assertEqual(self.skeleton.active_arrows, [])

    def test_does_not_shoot_while_frightened(self) -> None:
        """Verify a frightened skeleton cannot shoot.
        Check it shoots again once it is red.
        made by: Mohammad Abu Aresh
        """
        self.skeleton.frightened = True
        self.skeleton.shoot_arrow(self.player(5, 1), self.mape)
        self.assertEqual(self.skeleton.active_arrows, [])
        self.skeleton.frightened = False
        self.skeleton.shoot_arrow(self.player(5, 1), self.mape)
        self.assertEqual(len(self.skeleton.active_arrows), 1)

    def test_hit_is_reported_once_and_arrow_survives(self) -> None:
        """Verify one arrow reports a single hit on the player.
        Check the arrow keeps flying after the hit.
        made by: Mohammad Abu Aresh
        """
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
        """Verify the arrow stays active until it meets a wall.
        Check it is removed only after reaching the lane end.
        made by: Mohammad Abu Aresh
        """
        self.skeleton.shoot_arrow(self.player(10, 1), self.mape)
        player = self.player(10, 1)
        for _ in range(240):
            self.skeleton.update_arrows(player, self.mape, 1 / 60)
        self.assertTrue(all(a.active for a in self.skeleton.active_arrows))
        for _ in range(60):
            self.skeleton.update_arrows(player, self.mape, 1 / 60)
        self.assertLessEqual(len(self.skeleton.active_arrows), 1)

    def test_cooldown_and_single_arrow_limit(self) -> None:
        """Verify only one arrow exists at a time.
        Check the cooldown blocks an immediate second shot.
        made by: Mohammad Abu Aresh
        """
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
        """Verify resetting the AI removes every arrow.
        Check the shooting cooldown is cleared too.
        made by: Mohammad Abu Aresh
        """
        self.skeleton.shoot_arrow(self.player(10, 1), self.mape)
        self.skeleton.reset_ai()
        self.assertEqual(self.skeleton.active_arrows, [])
        self.assertEqual(self.skeleton.shoot_timer, 0.0)


if __name__ == "__main__":
    unittest.main()
