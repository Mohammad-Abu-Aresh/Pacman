import os
import unittest
from types import SimpleNamespace
from typing import Any

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from game.cheat_codes import apply_heart_cheat  # noqa: E402
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


if __name__ == "__main__":
    unittest.main()
