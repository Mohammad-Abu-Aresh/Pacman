import unittest
from unittest.mock import patch

from ghost_ai_fixtures import PATHING, PATHFINDER


class FrightenedPathTests(unittest.TestCase):
    def test_frightened_turn_avoids_reverse_when_an_exit_exists(self) -> None:
        """Reject ordinary reverse when another legal exit is available.
        Use a blocked random preference to exercise the fallback sequence.
        made by: Mohammad Abu Aresh
        """
        options = [(0, 1), (2, 1)]
        with patch.object(PATHING.random, "choice", return_value=(-1, 0)):
            step = PATHING.choose_frightened_step(
                (1, 1), (1, 0), options, False
            )
        self.assertEqual(step, (2, 1))

    def test_frightened_fallback_uses_arcade_direction_order(self) -> None:
        """Use up-left-down-right after a blocked random preference.
        Select up before later legal exits in the fallback sequence.
        made by: Mohammad Abu Aresh
        """
        options = [(2, 1), (1, 0), (0, 1)]
        with patch.object(PATHING.random, "choice", return_value=(0, 1)):
            step = PATHING.choose_frightened_step(
                (1, 1), (0, -1), options, False
            )
        self.assertEqual(step, (1, 0))

    def test_frightened_turn_honors_forced_reverse(self) -> None:
        """Honor a queued direction reversal when its cell is walkable.
        Do not let the pseudo-random preference override a forced reverse.
        made by: Mohammad Abu Aresh
        """
        options = [(0, 1), (1, 0)]
        step = PATHING.choose_frightened_step(
            (1, 1), (1, 0), options, True
        )
        self.assertEqual(step, (0, 1))

    def test_pathfinder_uses_bfs_to_return_through_open_cells(self) -> None:
        """Keep BFS available for the monster return-to-spawn route.
        Avoid walls and choose the first cell on a shortest legal path.
        made by: Mohammad Abu Aresh
        """
        grid = [
            [True, True, True, True, True],
            [True, False, False, False, True],
            [True, True, True, False, True],
            [True, True, True, False, True],
            [True, True, True, True, True],
        ]
        step = PATHFINDER.PathFinder.next_step(grid, (1, 1), (3, 3))
        self.assertEqual(step, (2, 1))

    def test_pathfinder_frightened_wrapper_uses_legal_neighbors(self) -> None:
        """Route frightened selection through PathFinder legal exits.
        Confirm the chosen cell is adjacent and open in the maze grid.
        made by: Mohammad Abu Aresh
        """
        grid = [
            [True, True, True, True, True],
            [True, False, False, False, True],
            [True, False, False, False, True],
            [True, False, False, False, True],
            [True, True, True, True, True],
        ]
        with patch.object(PATHING.random, "choice", return_value=(1, 0)):
            step = PATHFINDER.PathFinder.next_step_frightened(
                grid, (2, 2), (0, -1)
            )
        self.assertEqual(step, (3, 2))
        self.assertFalse(grid[step[1]][step[0]])


if __name__ == "__main__":
    unittest.main()
