import os
import unittest
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from game import gameengine as engine_module  # noqa: E402
from game import screens as screens_module  # noqa: E402
from game.game_modes import Mod  # noqa: E402
from game.gameengine import GameEngine  # noqa: E402
from game.name_entry import (  # noqa: E402
    add_character,
    cursor_text,
    final_name,
    remove_character,
    visible_text_area,
)
from game.screens import Screens  # noqa: E402

KEYS = SimpleNamespace(
    QUIT=0, KEYDOWN=1, K_BACKSPACE=8, K_RETURN=13, K_KP_ENTER=271,
    K_c=99, K_RIGHT=1, K_LEFT=2, K_UP=3, K_DOWN=4,
)


class NameRuleTests(unittest.TestCase):
    def test_printable_characters_are_added(self) -> None:
        """Verify typed letters, digits and symbols join the name.
        Check them one after the other.
        made by: Mohammad Abu Aresh
        """
        text = ""
        for char in "Ann_7":
            text = add_character(text, char)
        self.assertEqual(text, "Ann_7")

    def test_keys_without_a_character_are_ignored(self) -> None:
        """Verify arrow keys, controls and empty text change nothing.
        Their unicode text is empty or not printable.
        made by: Mohammad Abu Aresh
        """
        for char in ("", "\t", "\n", "\x1b", "ab"):
            self.assertEqual(add_character("Ann", char), "Ann")

    def test_the_name_is_limited_to_ten_characters(self) -> None:
        """Verify no character is added to a full name.
        Type twelve letters and read the result.
        made by: Mohammad Abu Aresh
        """
        text = ""
        for char in "abcdefghijkl":
            text = add_character(text, char)
        self.assertEqual(text, "abcdefghij")

    def test_spaces_are_only_allowed_inside_the_name(self) -> None:
        """Verify a name cannot start with a space or hold a double one.
        A single space between two words is accepted.
        made by: Mohammad Abu Aresh
        """
        self.assertEqual(add_character("", " "), "")
        self.assertEqual(add_character("Ann ", " "), "Ann ")
        self.assertEqual(add_character("Ann", " "), "Ann ")

    def test_backspace_removes_the_last_character(self) -> None:
        """Verify one removal drops one character.
        An empty name stays empty.
        made by: Mohammad Abu Aresh
        """
        self.assertEqual(remove_character("Ann"), "An")
        self.assertEqual(remove_character(""), "")

    def test_saved_name_is_trimmed_or_defaulted(self) -> None:
        """Verify an empty or blank name becomes the default name.
        A normal name only loses its outer spaces.
        made by: Mohammad Abu Aresh
        """
        self.assertEqual(final_name(""), "Player")
        self.assertEqual(final_name("   "), "Player")
        self.assertEqual(final_name(" Ann "), "Ann")
        self.assertEqual(final_name("Ann B"), "Ann B")

    def test_cursor_blinks_every_half_second(self) -> None:
        """Verify the cursor shows and hides in turns.
        Check the first two half seconds and the third.
        made by: Mohammad Abu Aresh
        """
        self.assertEqual(cursor_text("Ann", 0), "Ann|")
        self.assertEqual(cursor_text("Ann", 499), "Ann|")
        self.assertEqual(cursor_text("Ann", 500), "Ann")
        self.assertEqual(cursor_text("Ann", 1000), "Ann|")

    def test_long_text_keeps_its_end_visible(self) -> None:
        """Verify a text wider than the box is cut on the left.
        A short text is shown completely.
        made by: Mohammad Abu Aresh
        """
        self.assertEqual(visible_text_area(50, 100), (0, 50))
        self.assertEqual(visible_text_area(220, 76), (144, 76))


class EngineEntryTests(unittest.TestCase):
    def setUp(self) -> None:
        """Create an engine with a recording screens object.
        Restore the real screen mode after every test.
        made by: Mohammad Abu Aresh
        """
        engine: Any = GameEngine.__new__(GameEngine)
        engine.screens = SimpleNamespace(user_text="", addjson=MagicMock())
        engine.playr_score = 260
        engine.config = {"highscore_filename": "scores.json"}
        self.engine = engine
        self.old_state = Mod.state_variable
        self.addCleanup(setattr, Mod, "state_variable", self.old_state)

    def press(self, mode: int, *keys: tuple[int, str]) -> MagicMock:
        """Send key presses to the engine in the given screen mode.
        Return the mock that records the screen changes.
        made by: Mohammad Abu Aresh
        """
        Mod.state_variable = mode
        events = [
            SimpleNamespace(type=KEYS.KEYDOWN, key=key, unicode=char)
            for key, char in keys
        ]
        fake = SimpleNamespace(
            event=SimpleNamespace(get=lambda: events), **vars(KEYS)
        )
        with patch.object(engine_module, "pygame", fake), patch.object(
            Mod, "updatemod"
        ) as update_mod:
            self.engine.button_management()
        return update_mod

    def test_typing_builds_the_name_on_the_game_over_screen(self) -> None:
        """Verify typed letters appear in the stored name.
        Use the game over screen.
        made by: Mohammad Abu Aresh
        """
        self.press(Mod.GAME_OVER_SCREEN, (97, "A"), (98, "n"), (99, "n"))
        self.assertEqual(self.engine.screens.user_text, "Ann")

    def test_typing_also_works_on_the_victory_screen(self) -> None:
        """Verify the victory screen accepts the name the same way.
        Type two letters on it.
        made by: Mohammad Abu Aresh
        """
        self.press(Mod.VICTORY_SCREEN, (97, "A"), (98, "b"))
        self.assertEqual(self.engine.screens.user_text, "Ab")

    def test_backspace_edits_the_name(self) -> None:
        """Verify backspace removes the last typed letter.
        Type three letters and press it once.
        made by: Mohammad Abu Aresh
        """
        self.press(
            Mod.GAME_OVER_SCREEN,
            (97, "A"), (98, "b"), (99, "c"), (KEYS.K_BACKSPACE, "\b"),
        )
        self.assertEqual(self.engine.screens.user_text, "Ab")

    def test_enter_saves_the_name_with_the_final_score(self) -> None:
        """Verify enter saves the name and returns to the main menu.
        The typed text is cleared afterwards.
        made by: Mohammad Abu Aresh
        """
        update_mod = self.press(
            Mod.GAME_OVER_SCREEN, (97, "A"), (KEYS.K_RETURN, "\r")
        )
        self.engine.screens.addjson.assert_called_once_with(
            "A", 260, "scores.json"
        )
        self.assertEqual(self.engine.screens.user_text, "")
        update_mod.assert_called_once_with(Mod.MAIN_MENU_SCREEN)

    def test_keypad_enter_saves_too(self) -> None:
        """Verify the keypad enter key behaves like the main one.
        Check that a score was saved.
        made by: Mohammad Abu Aresh
        """
        self.press(Mod.VICTORY_SCREEN, (97, "A"), (KEYS.K_KP_ENTER, "\r"))
        self.engine.screens.addjson.assert_called_once()

    def test_empty_name_is_saved_with_the_default_name(self) -> None:
        """Verify pressing enter without typing saves a default name.
        An empty entry must never reach the score list.
        made by: Mohammad Abu Aresh
        """
        self.press(Mod.GAME_OVER_SCREEN, (KEYS.K_RETURN, "\r"))
        self.engine.screens.addjson.assert_called_once_with(
            "Player", 260, "scores.json"
        )

    def test_settings_screen_never_saves_a_score(self) -> None:
        """Verify enter and typing do nothing on the settings screen.
        A stale score must not be written from there.
        made by: Mohammad Abu Aresh
        """
        update_mod = self.press(
            Mod.SETTINGS_SCREEN, (97, "A"), (KEYS.K_RETURN, "\r")
        )
        self.engine.screens.addjson.assert_not_called()
        update_mod.assert_not_called()
        self.assertEqual(self.engine.screens.user_text, "")

    def test_arrow_keys_do_not_change_the_name(self) -> None:
        """Verify a key with no text leaves the name unchanged.
        An arrow key has an empty unicode value.
        made by: Mohammad Abu Aresh
        """
        with patch.object(engine_module.movement, "musle_memory"):
            self.press(Mod.GAME_OVER_SCREEN, (97, "A"), (KEYS.K_LEFT, ""))
        self.assertEqual(self.engine.screens.user_text, "A")


class FakeRect:
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        """Store the position and size of a fake rectangle.
        Provide the attributes the result screen reads.
        made by: Mohammad Abu Aresh
        """
        self.x, self.y = x, y
        self.width, self.height = width, height

    @property
    def centery(self) -> int:
        """Return the vertical middle of the rectangle.
        Use integer math like pygame does.
        made by: Mohammad Abu Aresh
        """
        return self.y + self.height // 2


class FakeSurface:
    def __init__(self, text: str) -> None:
        """Remember a rendered text and give it a size.
        Use twenty pixels per character and thirty pixels in height.
        made by: Mohammad Abu Aresh
        """
        self.text = text

    def get_width(self) -> int:
        """Return twenty pixels for every character of the text.
        The width decides whether the text must be cut.
        made by: Mohammad Abu Aresh
        """
        return len(self.text) * 20

    def get_height(self) -> int:
        """Return a fixed height of thirty pixels.
        Enough for centering the text in the box.
        made by: Mohammad Abu Aresh
        """
        return 30

    def get_rect(self, **kwargs: Any) -> FakeRect:
        """Return a rectangle centered on the requested point.
        Only the center keyword is supported.
        made by: Mohammad Abu Aresh
        """
        cx, cy = kwargs["center"]
        return FakeRect(cx - self.get_width() // 2, cy, self.get_width(), 30)


class FakeFont:
    def set_bold(self, flag: bool) -> None:
        """Accept the bold flag and ignore it.
        The fake text has no style.
        made by: Mohammad Abu Aresh
        """

    def render(self, text: str, smooth: bool, color: Any) -> FakeSurface:
        """Return a fake surface that remembers the text.
        Ignore the smoothing flag and the color.
        made by: Mohammad Abu Aresh
        """
        return FakeSurface(text)


class ResultScreenTests(unittest.TestCase):
    def draw(self, typed: str, ticks: int = 0, width: int = 1920) -> Any:
        """Draw the result screen once with a typed name.
        Return the mock screen that recorded every blit.
        made by: Mohammad Abu Aresh
        """
        screens: Any = Screens.__new__(Screens)
        screens.screen = MagicMock()
        screens.width, screens.height = width, 1080
        screens.user_text = "stale"
        fake = SimpleNamespace(
            font=SimpleNamespace(Font=lambda *args: FakeFont()),
            transform=SimpleNamespace(scale=lambda *args: "background"),
            draw=SimpleNamespace(rect=MagicMock()),
            time=SimpleNamespace(get_ticks=lambda: ticks),
            Rect=FakeRect,
        )
        with patch.object(screens_module, "pygame", fake):
            callback = screens.game_over_screen(260, False)
            screens.user_text = typed
            callback()
        return screens.screen

    def blits_with_text(self, screen: Any, prefix: str) -> list[Any]:
        """Return the blit calls that draw a text with the prefix.
        Only calls that carry a fake surface are inspected.
        made by: Mohammad Abu Aresh
        """
        return [
            call.args for call in screen.blit.call_args_list
            if hasattr(call.args[0], "text")
            and call.args[0].text.startswith(prefix)
        ]

    def test_typed_name_is_drawn_inside_the_input_box(self) -> None:
        """Verify the typed name is visible in the input box.
        Check the drawn text, its position and that it is not cut.
        made by: Mohammad Abu Aresh
        """
        screen = self.draw("Ann")
        drawn = self.blits_with_text(screen, "Ann")
        self.assertEqual(len(drawn), 1)
        surface, spot, clip = drawn[0]
        self.assertEqual(surface.text, "Ann|")
        self.assertEqual(spot[0], (1920 - 480) // 2 + 12)
        self.assertEqual((clip.x, clip.width), (0, 80))

    def test_cursor_is_hidden_in_the_second_half_of_the_blink(self) -> None:
        """Verify the cursor disappears in the second half second.
        The typed name itself stays on the screen.
        made by: Mohammad Abu Aresh
        """
        screen = self.draw("Ann", ticks=600)
        self.assertEqual(
            self.blits_with_text(screen, "Ann")[0][0].text, "Ann"
        )

    def test_empty_name_still_shows_the_cursor(self) -> None:
        """Verify the box shows a cursor before anything is typed.
        The player must see where the name will appear.
        made by: Mohammad Abu Aresh
        """
        screen = self.draw("")
        self.assertEqual(len(self.blits_with_text(screen, "|")), 1)

    def test_long_text_is_cut_to_fit_the_box(self) -> None:
        """Verify a name wider than the box shows only its end.
        Use a narrow screen so the box is small.
        made by: Mohammad Abu Aresh
        """
        screen = self.draw("Abcdefghij", width=400)
        surface, _, clip = self.blits_with_text(screen, "Abc")[0]
        self.assertEqual(clip.width, 100 - 24)
        self.assertEqual(clip.x, surface.get_width() - clip.width)

    def test_old_text_is_cleared_when_the_screen_is_created(self) -> None:
        """Verify text from an earlier game does not carry over.
        Check the stored text right after the screen is built.
        made by: Mohammad Abu Aresh
        """
        screens: Any = Screens.__new__(Screens)
        screens.screen = MagicMock()
        screens.width, screens.height = 1920, 1080
        screens.user_text = "stale"
        fake = SimpleNamespace(
            font=SimpleNamespace(Font=lambda *args: FakeFont()),
            transform=SimpleNamespace(scale=lambda *args: "background"),
            draw=SimpleNamespace(rect=MagicMock()),
            time=SimpleNamespace(get_ticks=lambda: 0),
            Rect=FakeRect,
        )
        with patch.object(screens_module, "pygame", fake):
            screens.game_over_screen(10, True)
        self.assertEqual(screens.user_text, "")


if __name__ == "__main__":
    unittest.main()
