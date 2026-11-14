import json
import os
import tempfile
import unittest
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from game import screens as screens_module  # noqa: E402
from game.overlay import names_panel_box, opacity_to_alpha  # noqa: E402
from game.screens import Screens  # noqa: E402


class FakeSurface:
    def __init__(self, text: str) -> None:
        """Remember the text that was rendered.
        Stand in for a pygame surface holding a line of text.
        made by: Mohammad Abu Aresh
        """
        self.text = text

    def get_rect(self, **kwargs: Any) -> Any:
        """Return the requested center as the rectangle.
        Enough for blitting a centered line of text.
        made by: Mohammad Abu Aresh
        """
        return kwargs["center"]


class FakeFont:
    def size(self, text: str) -> tuple[int, int]:
        """Return a width of ten pixels per character.
        Use a fixed height of twenty pixels.
        made by: Mohammad Abu Aresh
        """
        return len(text) * 10, 20

    def render(self, text: str, smooth: bool, color: Any) -> FakeSurface:
        """Return a fake surface that remembers the text.
        Ignore the smoothing flag and the color.
        made by: Mohammad Abu Aresh
        """
        return FakeSurface(text)


def make_screens() -> Any:
    """Build a screens object that draws on a mock screen.
    Use a full hd size for the layout.
    made by: Mohammad Abu Aresh
    """
    screens: Any = Screens.__new__(Screens)
    screens.screen = MagicMock()
    screens.width = 1920
    screens.height = 1080
    return screens


class OverlayMathTests(unittest.TestCase):
    def test_opacity_is_converted_to_alpha(self) -> None:
        """Verify the requested opacities become the right alpha.
        Check half opacity, seventy percent and the two limits.
        made by: Mohammad Abu Aresh
        """
        self.assertEqual(opacity_to_alpha(0.5), 128)
        self.assertEqual(opacity_to_alpha(0.7), 178)
        self.assertEqual(opacity_to_alpha(0.0), 0)
        self.assertEqual(opacity_to_alpha(1.0), 255)

    def test_opacity_is_clamped(self) -> None:
        """Verify an opacity outside zero and one stays valid.
        Check a negative and a too large value.
        made by: Mohammad Abu Aresh
        """
        self.assertEqual(opacity_to_alpha(-3.0), 0)
        self.assertEqual(opacity_to_alpha(4.0), 255)

    def test_panel_wraps_every_name_row(self) -> None:
        """Verify the panel is centered and covers all rows.
        Rows sit at 540 and 580 and the widest name is 300 wide.
        made by: Mohammad Abu Aresh
        """
        box = names_panel_box([200, 300], 960, 540, 40)
        self.assertEqual(box, (780, 505, 360, 110))
        assert box is not None
        self.assertLessEqual(box[1], 540 - 20)
        self.assertGreaterEqual(box[1] + box[3], 580 + 20)

    def test_panel_is_missing_without_names(self) -> None:
        """Verify no panel is created when there are no scores.
        An empty list of widths returns nothing.
        made by: Mohammad Abu Aresh
        """
        self.assertIsNone(names_panel_box([], 960, 540, 40))


class TopScoresPanelTests(unittest.TestCase):
    def run_screen(self, entries: list[dict[str, Any]]) -> tuple[Any, Any]:
        """Draw the top scores screen once for the given entries.
        Return the mock screen and the mocked shade factory.
        made by: Mohammad Abu Aresh
        """
        screens = make_screens()
        fake_pygame = SimpleNamespace(
            font=SimpleNamespace(Font=lambda *args: FakeFont()),
            transform=SimpleNamespace(smoothscale=lambda *args: "background"),
            draw=SimpleNamespace(rect=MagicMock()),
        )
        button = SimpleNamespace(rect=(0, 0, 1, 1), draw=lambda screen: False)
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "scores.json")
            with open(path, "w") as handle:
                json.dump(entries, handle)
            with patch.object(
                screens_module, "pygame", fake_pygame
            ), patch.object(
                screens_module, "Button", lambda **kwargs: button
            ), patch.object(
                screens_module, "make_shade", return_value="shade"
            ) as shade:
                screens.highscore_screen(path)()
        return screens.screen, shade

    def test_panel_is_drawn_behind_the_names_with_half_opacity(self) -> None:
        """Verify a half transparent black panel sits behind the names.
        Check its opacity, its position and that it is drawn first.
        made by: Mohammad Abu Aresh
        """
        entries = [{"name": "Ann", "score": 500}, {"name": "Bob", "score": 3}]
        screen, shade = self.run_screen(entries)
        widths = [len("1. Ann - 500 p") * 10, len("2. Bob - 3 p") * 10]
        box = names_panel_box(widths, 960, 540, 40)
        assert box is not None
        shade.assert_called_once_with(box[2:], 0.5)
        calls = [call.args for call in screen.blit.call_args_list]
        self.assertEqual(calls[0][0], "background")
        self.assertEqual(calls[1], ("shade", box[:2]))
        texts = [c[0].text for c in calls[2:] if hasattr(c[0], "text")]
        self.assertIn("1. Ann - 500 p", texts)

    def test_no_panel_without_scores(self) -> None:
        """Verify an empty score list draws no panel.
        Only the background is painted before the exit button.
        made by: Mohammad Abu Aresh
        """
        screen, shade = self.run_screen([])
        shade.assert_not_called()
        first = screen.blit.call_args_list[0].args[0]
        self.assertEqual(first, "background")


if __name__ == "__main__":
    unittest.main()
