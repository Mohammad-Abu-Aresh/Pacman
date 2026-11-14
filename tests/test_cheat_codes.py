import os
import unittest
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from game.cheat_codes import (  # noqa: E402
    apply_heart_cheat,
    apply_next_level_cheat,
)
from game.creature.player import Player  # noqa: E402


def make_game(lives: int = 3) -> Any:
    """Create a light game object holding a real player lives counter.
    Only the fields used by the heart cheat are provided.
    made by: Mohammad Abu Aresh
    """
    player = Player.__new__(Player)
    player._lives = lives
    controller = SimpleNamespace(player=player)
    return SimpleNamespace(
        player_creature=controller, lives=lives, heart_key_down=False
    )


class HeartCheatTests(unittest.TestCase):
    def test_pressing_the_key_adds_one_heart(self) -> None:
        """Verify one key press gives exactly one extra life.
        Check the player counter and the game life counter.
        made by: Mohammad Abu Aresh
        """
        game = make_game(3)
        self.assertTrue(apply_heart_cheat(game, True))
        self.assertEqual(game.player_creature.player._lives, 4)
        self.assertEqual(game.lives, 4)

    def test_holding_the_key_adds_only_one_heart(self) -> None:
        """Verify holding the key does not add a heart every frame.
        Check ten frames of a held key.
        made by: Mohammad Abu Aresh
        """
        game = make_game(3)
        for _ in range(10):
            apply_heart_cheat(game, True)
        self.assertEqual(game.lives, 4)

    def test_releasing_and_pressing_again_adds_another(self) -> None:
        """Verify a new press after a release adds a second heart.
        Check the total after two separate presses.
        made by: Mohammad Abu Aresh
        """
        game = make_game(3)
        apply_heart_cheat(game, True)
        apply_heart_cheat(game, False)
        apply_heart_cheat(game, True)
        self.assertEqual(game.lives, 5)

    def test_no_heart_without_the_key(self) -> None:
        """Verify nothing changes while the key is not pressed.
        The pressed flag is False when cheating mode is off.
        made by: Mohammad Abu Aresh
        """
        game = make_game(3)
        self.assertFalse(apply_heart_cheat(game, False))
        self.assertEqual(game.lives, 3)


class NextLevelCheatTests(unittest.TestCase):
    def game(self) -> Any:
        """Create a light game that counts its level changes.
        The next level method is a mock.
        made by: Mohammad Abu Aresh
        """
        return SimpleNamespace(next_key_down=False, next_level=MagicMock())

    def test_pressing_the_key_changes_the_level_once(self) -> None:
        """Verify one press jumps to the next level.
        Check that holding the key does not jump again.
        made by: Mohammad Abu Aresh
        """
        game = self.game()
        for _ in range(10):
            apply_next_level_cheat(game, True)
        game.next_level.assert_called_once()

    def test_every_new_press_changes_the_level(self) -> None:
        """Verify releasing and pressing again jumps once more.
        Check two separate presses.
        made by: Mohammad Abu Aresh
        """
        game = self.game()
        apply_next_level_cheat(game, True)
        apply_next_level_cheat(game, False)
        apply_next_level_cheat(game, True)
        self.assertEqual(game.next_level.call_count, 2)

    def test_no_jump_without_the_key(self) -> None:
        """Verify nothing happens while the key is not pressed.
        The pressed flag is False when the cheating mode is off.
        made by: Mohammad Abu Aresh
        """
        game = self.game()
        self.assertFalse(apply_next_level_cheat(game, False))
        game.next_level.assert_not_called()


if __name__ == "__main__":
    unittest.main()
