import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def load_module(module_name: str, relative_path: str) -> ModuleType:
    """Load a dependency-light helper directly from its source file.
    Register the module before execution so dataclass type processing works.
    made by: Mohammad Abu Aresh
    """
    source = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, source)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module: {relative_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


MODES: Any = load_module(
    "pacman_test_ghost_modes", "game/creature/ghost_modes.py"
)
LIFECYCLE: Any = load_module(
    "pacman_test_ghost_lifecycle", "game/creature/ghost_lifecycle.py"
)
PATHING: Any = load_module(
    "pacman_test_ghost_pathing", "game/creature/ghost_pathing.py"
)

PATHFINDER_PACKAGE = "pacman_test_pathfinder"
package = ModuleType(PATHFINDER_PACKAGE)
setattr(package, "__path__", [])
sys.modules[PATHFINDER_PACKAGE] = package
player_module = ModuleType(f"{PATHFINDER_PACKAGE}.player")
setattr(player_module, "Direction", type(
    "Direction",
    (),
    {
        "up": (0, -1),
        "left": (-1, 0),
        "down": (0, 1),
        "right": (1, 0),
    },
))
sys.modules[player_module.__name__] = player_module
sys.modules[f"{PATHFINDER_PACKAGE}.ghost_pathing"] = PATHING
PATHFINDER: Any = load_module(
    f"{PATHFINDER_PACKAGE}.bfs", "game/creature/bfs.py"
)


class FakePlayer:
    def __init__(self) -> None:
        """Initialize the score and Super-state fields used by the helpers.
        Keep the fake player independent from Pygame and the main game loop.
        made by: Mohammad Abu Aresh
        """
        self._is_super = False
        self.score = 0

    def eat(self, points: int) -> int:
        """Add points to the test player's score.
        Return the updated score to match the production Player interface.
        made by: Mohammad Abu Aresh
        """
        self.score += points
        return self.score


class FakeMonster:
    MODE_SCHEDULE: tuple[tuple[str, float], ...]

    def __init__(self, spawn_point: tuple[int, int]) -> None:
        """Initialize lifecycle and movement fields used by ghost helpers.
        Keep the fake image as a string so tests do not require a display.
        made by: Mohammad Abu Aresh
        """
        self.spawn_point = spawn_point
        self.x, self.y = map(float, spawn_point)
        self.lifecycle = LIFECYCLE.GhostLifecycle()
        self.live = True
        self.is_following = True
        self.target_point: tuple[int, int] | None = None
        self.next_point: tuple[int, int] | None = None
        self.movement_direction = (0, 0)
        self.reverse_pending = False
        self.frightened = False
        self.frightened_timer = 0.0
        self.mode = "scatter"
        self.mode_timer = 7.0
        self.image = "normal"
        self.reset_count = 0

    def activate_frightened(self, duration: float) -> None:
        """Set the fake monster to its frightened state.
        Record the timer and blue visual for lifecycle assertions.
        made by: Mohammad Abu Aresh
        """
        self.frightened = True
        self.frightened_timer = max(self.frightened_timer, duration)
        self.image = "blue"
        self.reverse_pending = True

    def die(self) -> None:
        """Mark the fake monster as returning to its spawn.
        Store the target and stop its cached movement step.
        made by: Mohammad Abu Aresh
        """
        self.live = False
        self.is_following = False
        self.target_point = self.spawn_point
        self.next_point = None

    def load_size(self) -> None:
        """Restore the fake monster's normal sprite marker.
        Match the production method called after reaching the spawn.
        made by: Mohammad Abu Aresh
        """
        self.image = "normal"

    def reset_ai(self) -> None:
        """Count AI reset requests from the level schedule helper.
        Keep the fake reset operation deterministic for unit tests.
        made by: Mohammad Abu Aresh
        """
        self.reset_count += 1


class FakeController:
    def __init__(self) -> None:
        """Create the player and four monsters used by group logic.
        Initialize the shared frightened timer and Power Pellet cycle.
        made by: Mohammad Abu Aresh
        """
        self.player = FakePlayer()
        self.BabyZombie = FakeMonster((1, 1))
        self.Skeleton = FakeMonster((2, 2))
        self.Enderman = FakeMonster((3, 3))
        self.witch = FakeMonster((4, 4))
        self.frightened_timer = 0.0
        self.frightened_cycle = 0
