import os
import unittest
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from game import scene_layers as layers_module  # noqa: E402
from game.block import Block  # noqa: E402
from game.overlay import maze_backdrop_box  # noqa: E402


def make_game(rows: int, columns: int) -> Any:
    """Build a light game with a maze of the given size.
    Only the grid and the map origin are provided.
    made by: Mohammad Abu Aresh
    """
    grid = [[False] * columns for _ in range(rows)]
    return SimpleNamespace(
        maze_map=SimpleNamespace(every_cell=grid, origin_x=100, origin_y=50)
    )


class BackdropTests(unittest.TestCase):
    def setUp(self) -> None:
        """Set the block size and empty the cached backdrop surface.
        Restore the real size after every test.
        made by: Mohammad Abu Aresh
        """
        self.old_size = Block.size
        Block.size = 40
        layers_module._backdrop_shade.cache_clear()
        self.addCleanup(setattr, Block, "size", self.old_size)
        self.addCleanup(layers_module._backdrop_shade.cache_clear)

    def test_box_covers_the_whole_maze_footprint(self) -> None:
        """Verify the backdrop rectangle matches the maze size.
        Check the position and the size for a small maze.
        made by: Mohammad Abu Aresh
        """
        box = maze_backdrop_box(10, 20, (100, 50), 40)
        self.assertEqual(box, (122, 65, 800, 408))

    def test_backdrop_is_seventy_percent_black(self) -> None:
        """Verify the maze backdrop uses an opacity of seventy percent.
        A faint trace of the level image must stay visible.
        made by: Mohammad Abu Aresh
        """
        screen = MagicMock()
        with patch.object(
            layers_module, "Images", SimpleNamespace(screen=screen)
        ), patch.object(
            layers_module, "make_shade", return_value="shade"
        ) as shade:
            layers_module.draw_backdrop(make_game(10, 20))
        shade.assert_called_once_with((800, 408), 0.7)
        screen.blit.assert_called_once_with("shade", (122, 65))

    def test_backdrop_surface_is_built_only_once_per_size(self) -> None:
        """Verify the translucent surface is cached between frames.
        Draw twice and count the surface builds.
        made by: Mohammad Abu Aresh
        """
        with patch.object(
            layers_module, "Images", SimpleNamespace(screen=MagicMock())
        ), patch.object(
            layers_module, "make_shade", return_value="shade"
        ) as shade:
            game = make_game(10, 20)
            layers_module.draw_backdrop(game)
            layers_module.draw_backdrop(game)
        shade.assert_called_once()


if __name__ == "__main__":
    unittest.main()
