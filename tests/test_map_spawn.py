import contextlib
import importlib.util
import io
import sys
import unittest
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
WHEEL = ROOT / "mazegenerator-2.1.0-py3-none-any.whl"
sys.path.insert(0, str(WHEEL))
MazeGenerator = getattr(
    importlib.import_module("mazegenerator"), "MazeGenerator"
)

class FakeImages:
    width = 1920
    height = 1080


photos_package = ModuleType("photos")
setattr(photos_package, "__path__", [])
images_module = ModuleType("photos.loderimages")
setattr(images_module, "Images", FakeImages)
previous_photos = sys.modules.get("photos")
previous_images = sys.modules.get("photos.loderimages")
sys.modules["photos"] = photos_package
sys.modules["photos.loderimages"] = images_module
try:
    spec = importlib.util.spec_from_file_location(
        "pacman_map_spawn_test", ROOT / "game" / "block.py"
    )
    if spec is None or spec.loader is None:
        raise ImportError("Unable to load the map module for spawn tests")
    MAP_MODULE = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = MAP_MODULE
    spec.loader.exec_module(MAP_MODULE)
finally:
    if previous_photos is None:
        sys.modules.pop("photos", None)
    else:
        sys.modules["photos"] = previous_photos
    if previous_images is None:
        sys.modules.pop("photos.loderimages", None)
    else:
        sys.modules["photos.loderimages"] = previous_images
Mape = getattr(MAP_MODULE, "Mape")


class MapSpawnTests(unittest.TestCase):
    def test_walkable_center_is_kept(self) -> None:
        """Keep the exact geometric center when it is walkable.
        Avoid shifting the player's intended start point unnecessarily.
        made by: Mohammad Abu Aresh
        """
        grid = [
            [True, True, True, True, True],
            [True, False, False, False, True],
            [True, False, False, False, True],
            [True, False, False, False, True],
            [True, True, True, True, True],
        ]
        self.assertEqual(Mape._center_spawn_point(grid), (2, 2))

    def test_blocked_center_uses_nearest_walkable_cell(self) -> None:
        """Move the spawn to the nearest legal cell when center is blocked.
        Resolve equal-distance candidates with deterministic tie-breaking.
        made by: Mohammad Abu Aresh
        """
        grid = [[True] * 5 for _ in range(5)]
        grid[2][1] = False
        grid[2][3] = False
        self.assertEqual(Mape._center_spawn_point(grid), (1, 2))

    def test_empty_grid_is_rejected(self) -> None:
        """Reject an empty grid instead of returning invalid coordinates.
        Keep malformed maze data from producing a wall spawn position.
        made by: Mohammad Abu Aresh
        """
        with self.assertRaises(ValueError):
            Mape._center_spawn_point([])

    def test_grid_without_walkable_cells_is_rejected(self) -> None:
        """Reject a maze that contains no legal player spawn cell.
        Fail explicitly rather than placing the player inside a wall.
        made by: Mohammad Abu Aresh
        """
        grid = [[True, True], [True, True]]
        with self.assertRaises(ValueError):
            Mape._center_spawn_point(grid)

    def test_spawn_is_walkable_across_level_dimensions(self) -> None:
        """Keep the player spawn walkable across growing maze dimensions.
        Cover seeds where the previous point and exact center are blocked.
        made by: Mohammad Abu Aresh
        """
        cases = (
            ((11, 7), 1),
            ((13, 8), 4),
            ((15, 9), 1),
            ((17, 10), 13),
            ((19, 11), 21),
            ((21, 12), 34),
            ((23, 13), 55),
        )
        for size, seed in cases:
            with contextlib.redirect_stdout(io.StringIO()):
                maze = MazeGenerator(size=size, seed=seed)
            map_data = Mape(maze)
            spawn_x, spawn_y = map_data.spawn_point["player"]
            self.assertFalse(
                map_data.grid[spawn_y][spawn_x],
                msg=f"Blocked spawn for size={size}, seed={seed}",
            )

    def test_spawn_stays_valid_for_multiple_seeds(self) -> None:
        """Check multiple generated maps at each supported size progression.
        Ensure every selected player position refers to an open grid cell.
        made by: Mohammad Abu Aresh
        """
        for size in ((11, 7), (13, 8), (15, 9), (17, 10), (19, 11)):
            for seed in range(1, 21):
                with contextlib.redirect_stdout(io.StringIO()):
                    maze = MazeGenerator(size=size, seed=seed)
                map_data = Mape(maze)
                spawn_x, spawn_y = map_data.spawn_point["player"]
                self.assertFalse(
                    map_data.grid[spawn_y][spawn_x],
                    msg=f"Blocked spawn for size={size}, seed={seed}",
                )


if __name__ == "__main__":
    unittest.main()
