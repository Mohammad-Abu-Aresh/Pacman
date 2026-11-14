import os
import unittest
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from game import gameplay as gameplay_module  # noqa: E402
from game.creature.effects import ParticleEffects  # noqa: E402
from game.gameplay import GameSystem  # noqa: E402
from game.level_intro import LevelIntro  # noqa: E402
from game.pause_menu import PauseMenu  # noqa: E402
from pygame_fakes import fake_pygame  # noqa: E402


def make_game(collision: bool, arrow: bool) -> Any:
    """Build a running game whose frame reports the given hits.
    The intro is finished and every monster is a light stand in.
    made by: Mohammad Abu Aresh
    """
    game: Any = GameSystem.__new__(GameSystem)
    game.intro = LevelIntro()
    game.intro.update(60.0)
    game.pause = PauseMenu(1920, 1080)
    game.heart_key_down = False
    game.next_key_down = False
    game.wait_timer = 0.0
    game.time_left = 90.0
    game.config = {}
    game.maze_map = SimpleNamespace(every_cell=[[False]])
    player = SimpleNamespace(
        x=1.0, y=1.0, change_diric=MagicMock(), move=MagicMock()
    )
    game.player_creature = SimpleNamespace(
        player=player,
        BabyZombie=MagicMock(),
        Skeleton=MagicMock(),
        Enderman=MagicMock(),
        witch=MagicMock(),
        effects=ParticleEffects(),
        update_frightened=MagicMock(),
        check_collision=MagicMock(return_value=collision),
        update_abilities=MagicMock(return_value=arrow),
    )
    return game


class DeathRuleTests(unittest.TestCase):
    def frame(self, game: Any, cheating: bool) -> MagicMock:
        """Run one gameplay frame and return the death handler mock.
        Block the gum logic so only the hit rules are exercised.
        made by: Mohammad Abu Aresh
        """
        with patch.object(
            gameplay_module, "pygame", fake_pygame(set())
        ), patch.object(
            GameSystem, "_eat_pacgums", return_value=False
        ), patch.object(
            GameSystem, "_handle_player_death"
        ) as death:
            game.update(1 / 60, cheating)
        return death

    def test_monster_contact_kills_the_player(self) -> None:
        """Verify a dangerous contact starts the death handling.
        The cheating mode is off.
        made by: Mohammad Abu Aresh
        """
        self.assertTrue(self.frame(make_game(True, False), False).called)

    def test_arrow_hit_kills_the_player(self) -> None:
        """Verify an arrow hit starts the death handling.
        The cheating mode is off.
        made by: Mohammad Abu Aresh
        """
        self.assertTrue(self.frame(make_game(False, True), False).called)

    def test_cheating_ignores_monster_contact(self) -> None:
        """Verify the cheating mode is the only exception to the contact.
        The death handling must not start.
        made by: Mohammad Abu Aresh
        """
        self.assertFalse(self.frame(make_game(True, False), True).called)

    def test_cheating_ignores_arrow_hits(self) -> None:
        """Verify the cheating mode also ignores arrow hits.
        The death handling must not start.
        made by: Mohammad Abu Aresh
        """
        self.assertFalse(self.frame(make_game(False, True), True).called)

    def test_no_hit_means_no_death(self) -> None:
        """Verify a quiet frame never starts the death handling.
        Neither a contact nor an arrow is reported.
        made by: Mohammad Abu Aresh
        """
        self.assertFalse(self.frame(make_game(False, False), False).called)


if __name__ == "__main__":
    unittest.main()
