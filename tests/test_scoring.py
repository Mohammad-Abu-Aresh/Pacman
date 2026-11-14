import os
import unittest
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from game import game_renderer as renderer_module  # noqa: E402
from game.gameplay import GameSystem  # noqa: E402
from game.scoring import final_score, score_multiplier_label  # noqa: E402


def make_game(score: int, hardcore: bool) -> Any:
    """Build a light game with a player score and a recording font.
    The font returns the rendered text instead of a surface.
    made by: Mohammad Abu Aresh
    """
    game: Any = GameSystem.__new__(GameSystem)
    game.hardcore_mode = hardcore
    game.player_creature = SimpleNamespace(
        player=SimpleNamespace(score=score)
    )
    game.font = SimpleNamespace(
        size=lambda text: (len(text) * 10, 20),
        render=lambda text, smooth, color: text,
    )
    return game


class FinalScoreTests(unittest.TestCase):
    def test_hardcore_points_are_multiplied_by_one_point_three(self) -> None:
        """Verify hardcore points become one point three times larger.
        Check several values that are multiples of ten.
        made by: Mohammad Abu Aresh
        """
        self.assertEqual(final_score(100, True), 130)
        self.assertEqual(final_score(10, True), 13)
        self.assertEqual(final_score(70, True), 91)
        self.assertEqual(final_score(2000, True), 2600)

    def test_normal_points_stay_the_same(self) -> None:
        """Verify the normal mode keeps the collected points.
        Check zero and a regular value.
        made by: Mohammad Abu Aresh
        """
        self.assertEqual(final_score(100, False), 100)
        self.assertEqual(final_score(0, False), 0)

    def test_zero_points_stay_zero_in_hardcore(self) -> None:
        """Verify the multiplier does not invent points.
        A player without points keeps a zero score.
        made by: Mohammad Abu Aresh
        """
        self.assertEqual(final_score(0, True), 0)

    def test_the_multiplier_label_only_exists_in_hardcore(self) -> None:
        """Verify the text next to the counter is x 1.3 in hardcore.
        Check that the normal mode shows nothing.
        made by: Mohammad Abu Aresh
        """
        self.assertEqual(score_multiplier_label(True), "x 1.3")
        self.assertEqual(score_multiplier_label(False), "")


class GameScoreTests(unittest.TestCase):
    def test_game_reports_the_multiplied_score_in_hardcore(self) -> None:
        """Verify the score read by the engine is the final score.
        The engine saves it for both victory and game over.
        made by: Mohammad Abu Aresh
        """
        self.assertEqual(make_game(200, True).points(), 260)

    def test_game_reports_the_plain_score_in_normal_mode(self) -> None:
        """Verify the normal mode reports the collected points.
        No multiplier is applied.
        made by: Mohammad Abu Aresh
        """
        self.assertEqual(make_game(200, False).points(), 200)

    def draw(self, game: Any) -> list[str]:
        """Draw the score counter and return every rendered text.
        Replace the screen by a mock so nothing is painted.
        made by: Mohammad Abu Aresh
        """
        fake_images = SimpleNamespace(screen=MagicMock())
        with patch.object(renderer_module, "Images", fake_images):
            renderer_module.draw_score(game, 10, 10)
        calls = fake_images.screen.blit.call_args_list
        return [call.args[0] for call in calls]

    def test_counter_shows_the_plain_points_with_the_label(self) -> None:
        """Verify the counter itself is not multiplied in hardcore.
        Check the label x 1.3 is drawn next to it.
        made by: Mohammad Abu Aresh
        """
        texts = self.draw(make_game(100, True))
        self.assertIn("Score: 100", texts)
        self.assertNotIn("Score: 130", texts)
        self.assertIn("x 1.3", texts)

    def test_counter_has_no_label_in_normal_mode(self) -> None:
        """Verify the normal mode draws only the score text.
        No multiplier label may appear.
        made by: Mohammad Abu Aresh
        """
        texts = self.draw(make_game(100, False))
        self.assertIn("Score: 100", texts)
        self.assertNotIn("x 1.3", texts)


if __name__ == "__main__":
    unittest.main()
