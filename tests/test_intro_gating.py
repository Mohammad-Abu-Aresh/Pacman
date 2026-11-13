import os
import unittest
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from game import gameplay as gameplay_module  # noqa: E402
from game import pause_menu as pause_module  # noqa: E402
from game.creature.effects import ParticleEffects  # noqa: E402
from game.gameplay import GameSystem  # noqa: E402
from game.level_intro import LevelIntro  # noqa: E402
from game.pause_menu import PauseMenu  # noqa: E402


def make_game() -> Any:
    """Build a game object that is frozen by a fresh level intro.
    Only the fields read before the gameplay update are provided.
    made by: Mohammad Abu Aresh
    """
    game: Any = GameSystem.__new__(GameSystem)
    game.intro = LevelIntro()
    game.wait_timer = 0.0
    game.heart_key_down = False
    game.pause = PauseMenu(1920, 1080)
    game.time_left = 90.0
    game.lives = 3
    game.mobs = tuple(SimpleNamespace(x=1.0, y=1.0) for _ in range(5))
    game.player_creature = SimpleNamespace(
        effects=ParticleEffects(), player=MagicMock()
    )
    return game


def fake_pygame(pressed: set[str]) -> Any:
    """Create a stand in for pygame with a chosen set of pressed keys.
    The key state is a plain tuple indexed by the fake key constants.
    made by: Mohammad Abu Aresh
    """
    index = {"h": 0, "esc": 1, "n": 2, "x": 3}
    flags = tuple(i in {index[name] for name in pressed} for i in range(4))
    return SimpleNamespace(
        key=SimpleNamespace(get_pressed=lambda: flags),
        K_h=0,
        K_ESCAPE=1,
        K_n=2,
    )


class IntroGatingTests(unittest.TestCase):
    def test_level_timer_and_player_stay_frozen_during_intro(self) -> None:
        """Verify the level timer and the player do not move in the intro.
        Check one update that is shorter than the intro.
        made by: Mohammad Abu Aresh
        """
        game = make_game()
        with patch.object(gameplay_module, "pygame", fake_pygame(set())):
            game.update(0.5)
        self.assertEqual(game.time_left, 90.0)
        game.player_creature.player.move.assert_not_called()

    def test_spawn_particles_keep_running_during_intro(self) -> None:
        """Verify spawn bursts are created while the gameplay is frozen.
        The player spawns at four seconds into the intro.
        made by: Mohammad Abu Aresh
        """
        game = make_game()
        with patch.object(gameplay_module, "pygame", fake_pygame(set())):
            game.update(3.99)
            game.update(0.01)
        self.assertEqual(len(game.player_creature.effects.particles), 14)

    def test_escape_pauses_the_game_during_intro(self) -> None:
        """Verify escape pauses the intro instead of leaving the game.
        Check that the intro clock does not advance while paused.
        made by: Mohammad Abu Aresh
        """
        game = make_game()
        with patch.object(gameplay_module, "pygame", fake_pygame({"esc"})):
            game.update(0.5)
        self.assertTrue(game.pause.active)
        self.assertEqual(game.intro.elapsed, 0.0)

    def test_paused_game_ignores_time_and_cheat_keys(self) -> None:
        """Verify nothing advances while the game is paused.
        The heart cheat is ignored during the pause as well.
        made by: Mohammad Abu Aresh
        """
        game = make_game()
        game.pause.active = True
        game.pause.esc_down = True
        mouse = SimpleNamespace(
            mouse=SimpleNamespace(
                get_pressed=lambda: (False, False, False),
                get_pos=lambda: (0, 0),
            )
        )
        with patch.object(
            gameplay_module, "pygame", fake_pygame({"h"})
        ), patch.object(pause_module, "pygame", mouse):
            game.update(1.0, True)
        self.assertEqual(game.intro.elapsed, 0.0)
        game.player_creature.player.add_life.assert_not_called()

    def test_heart_cheat_works_during_intro(self) -> None:
        """Verify the heart cheat key is read before the intro freeze.
        The key adds one life while the level is still hidden.
        made by: Mohammad Abu Aresh
        """
        game = make_game()
        with patch.object(gameplay_module, "pygame", fake_pygame({"h"})):
            game.update(0.5, True)
        game.player_creature.player.add_life.assert_called_once()


if __name__ == "__main__":
    unittest.main()
