import os
import unittest
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from game.creature import player as player_module  # noqa: E402
from game.creature.player import Direction, Player  # noqa: E402
from game.creature.step_probe import probe_cell  # noqa: E402


def make_player(x: float, y: float, rows: list[str]) -> Any:
    """Create a player on a text maze without running his constructor.
    A hash is a wall, a dot is open and the speed is seven percent.
    made by: Mohammad Abu Aresh
    """
    player: Any = Player.__new__(Player)
    grid = [[char == "#" for char in row] for row in rows]
    player.maze = SimpleNamespace(every_cell=grid)
    player.x, player.y = x, y
    player.locaion = (x, y)
    player.speed = 0.07
    return player


def walk(player: Any, direction: tuple[int, int], steps: int) -> MagicMock:
    """Move the player for a number of frames in one direction.
    Return the mock that records the traffic updates.
    made by: Mohammad Abu Aresh
    """
    fake = SimpleNamespace(move=direction, traffic_update=MagicMock())
    with patch.object(player_module, "movement", fake):
        for _ in range(steps):
            player.move()
    return fake.traffic_update


CORRIDOR = ["#######", "#.....#", "#######"]
COLUMN = ["###", "#.#", "#.#", "#.#", "#.#", "###"]


class ProbeCellTests(unittest.TestCase):
    def test_probe_looks_half_a_cell_ahead_to_the_right(self) -> None:
        """Verify the probe at a cell center reaches the next cell.
        Check the center and a position just before it.
        made by: Mohammad Abu Aresh
        """
        self.assertEqual(probe_cell(3.0, 1.0, 1, 0), (4, 1))
        self.assertEqual(probe_cell(2.93, 1.0, 1, 0), (3, 1))

    def test_probe_looks_half_a_cell_ahead_to_the_left(self) -> None:
        """Verify the left probe is the mirror of the right probe.
        Check the center and a position just before it.
        made by: Mohammad Abu Aresh
        """
        self.assertEqual(probe_cell(3.0, 1.0, -1, 0), (2, 1))
        self.assertEqual(probe_cell(3.07, 1.0, -1, 0), (3, 1))

    def test_probe_works_on_the_vertical_axis(self) -> None:
        """Verify going down and up probe the next row.
        The other axis keeps the nearest cell.
        made by: Mohammad Abu Aresh
        """
        self.assertEqual(probe_cell(2.0, 3.0, 0, 1), (2, 4))
        self.assertEqual(probe_cell(2.0, 3.0, 0, -1), (2, 2))
        self.assertEqual(probe_cell(2.1, 3.0, 0, 1), (2, 4))


class StopAtCenterTests(unittest.TestCase):
    def test_stops_at_the_center_before_a_wall_on_the_right(self) -> None:
        """Verify Steve stops exactly at the center of the last open cell.
        Walk right in a corridor that ends with a wall.
        made by: Mohammad Abu Aresh
        """
        player = make_player(1.0, 1.0, CORRIDOR)
        traffic = walk(player, Direction.right, 120)
        self.assertEqual((player.x, player.y), (5.0, 1.0))
        traffic.assert_called_with(Direction.none)

    def test_stops_at_the_center_before_a_wall_on_the_left(self) -> None:
        """Verify the same centered stop when walking left.
        The first open cell is the last stop.
        made by: Mohammad Abu Aresh
        """
        player = make_player(5.0, 1.0, CORRIDOR)
        walk(player, Direction.left, 120)
        self.assertEqual((player.x, player.y), (1.0, 1.0))

    def test_stops_at_the_center_going_down_and_up(self) -> None:
        """Verify the centered stop on the vertical axis.
        Walk to the bottom and back to the top of a column.
        made by: Mohammad Abu Aresh
        """
        player = make_player(1.0, 1.0, COLUMN)
        walk(player, Direction.down, 120)
        self.assertEqual((player.x, player.y), (1.0, 4.0))
        walk(player, Direction.up, 120)
        self.assertEqual((player.x, player.y), (1.0, 1.0))

    def test_never_enters_the_wall_cell(self) -> None:
        """Verify Steve never crosses the half way line of a wall cell.
        Track the position on every frame of the walk.
        made by: Mohammad Abu Aresh
        """
        player = make_player(1.0, 1.0, CORRIDOR)
        fake = SimpleNamespace(
            move=Direction.right, traffic_update=MagicMock()
        )
        with patch.object(player_module, "movement", fake):
            for _ in range(120):
                player.move()
                self.assertLessEqual(player.x, 5.0)

    def test_dead_end_keeps_steve_on_the_center(self) -> None:
        """Verify pushing into a wall from the center does not move him.
        The position stays on the center of the cell.
        made by: Mohammad Abu Aresh
        """
        player = make_player(5.0, 1.0, CORRIDOR)
        walk(player, Direction.right, 10)
        self.assertEqual((player.x, player.y), (5.0, 1.0))

    def test_stop_recenters_a_player_that_was_off_center(self) -> None:
        """Verify an off center start still ends on a cell center.
        Start a little after a center and walk into the wall.
        made by: Mohammad Abu Aresh
        """
        player = make_player(2.3, 1.0, CORRIDOR)
        walk(player, Direction.right, 120)
        self.assertEqual(player.x, 5.0)

    def test_maze_border_stops_him_on_the_center_too(self) -> None:
        """Verify the edge of the grid works like a wall.
        The outside cell is not walkable.
        made by: Mohammad Abu Aresh
        """
        player = make_player(1.0, 1.0, ["....", "....", "...."])
        walk(player, Direction.left, 40)
        self.assertEqual(player.x, 0.0)

    def test_open_road_does_not_stop_him(self) -> None:
        """Verify a free corridor lets Steve move without interruptions.
        Check that no stop was reported and he advanced.
        made by: Mohammad Abu Aresh
        """
        player = make_player(1.0, 1.0, CORRIDOR)
        traffic = walk(player, Direction.right, 20)
        traffic.assert_not_called()
        self.assertAlmostEqual(player.x, 1.0 + 20 * 0.07)


if __name__ == "__main__":
    unittest.main()
