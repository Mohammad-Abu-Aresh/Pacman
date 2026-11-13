import os
import unittest
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from game import pause_menu as pause_module  # noqa: E402
from game.pause_menu import PauseMenu, contains  # noqa: E402


def fake_mouse(down: bool, position: tuple[int, int]) -> Any:
    """Create a stand in for pygame with a chosen mouse state.
    The left button is down or up and the cursor is at the position.
    made by: Mohammad Abu Aresh
    """
    return SimpleNamespace(
        mouse=SimpleNamespace(
            get_pressed=lambda: (down, False, False),
            get_pos=lambda: position,
        )
    )


def center_of(box: tuple[int, int, int, int]) -> tuple[int, int]:
    """Return the middle point of a rectangle tuple.
    Use it to click inside a button.
    made by: Mohammad Abu Aresh
    """
    return box[0] + box[2] // 2, box[1] + box[3] // 2


class PauseMenuTests(unittest.TestCase):
    def setUp(self) -> None:
        """Create a pause menu for a full hd screen.
        Run it before every pause menu test.
        made by: Mohammad Abu Aresh
        """
        self.menu = PauseMenu(1920, 1080)

    def click(self, position: tuple[int, int]) -> None:
        """Press and release the left mouse button at a position.
        Run two updates because a click needs an up then a down state.
        made by: Mohammad Abu Aresh
        """
        with patch.object(pause_module, "pygame", fake_mouse(False, position)):
            self.menu.update(False)
        with patch.object(pause_module, "pygame", fake_mouse(True, position)):
            self.menu.update(False)

    def test_escape_pauses_the_game(self) -> None:
        """Verify a new escape press activates the pause.
        The update must report that the game stays frozen.
        made by: Mohammad Abu Aresh
        """
        self.assertTrue(self.menu.update(True))
        self.assertTrue(self.menu.active)

    def test_holding_escape_toggles_only_once(self) -> None:
        """Verify a held escape key does not flicker the pause.
        Check several frames with the key still down.
        made by: Mohammad Abu Aresh
        """
        for _ in range(5):
            with patch.object(
                pause_module, "pygame", fake_mouse(False, (0, 0))
            ):
                self.menu.update(True)
        self.assertTrue(self.menu.active)

    def test_second_escape_press_resumes(self) -> None:
        """Verify pressing escape again continues the game.
        Release the key between both presses.
        made by: Mohammad Abu Aresh
        """
        self.menu.update(True)
        with patch.object(pause_module, "pygame", fake_mouse(False, (0, 0))):
            self.menu.update(False)
        self.assertFalse(self.menu.update(True))
        self.assertFalse(self.menu.active)

    def test_inactive_menu_does_not_freeze(self) -> None:
        """Verify a game that is not paused keeps running.
        Check an update without any key pressed.
        made by: Mohammad Abu Aresh
        """
        self.assertFalse(self.menu.update(False))

    def test_clicking_resume_continues_the_game(self) -> None:
        """Verify the resume button ends the pause.
        Click in the middle of the button.
        made by: Mohammad Abu Aresh
        """
        self.menu.update(True)
        self.click(center_of(self.menu.resume_box))
        self.assertFalse(self.menu.active)

    def test_clicking_outside_the_buttons_keeps_the_pause(self) -> None:
        """Verify a click away from the buttons does nothing.
        Click in the top left corner of the screen.
        made by: Mohammad Abu Aresh
        """
        self.menu.update(True)
        self.click((5, 5))
        self.assertTrue(self.menu.active)

    def test_mouse_held_when_pausing_does_not_click(self) -> None:
        """Verify a mouse button held during the pause start is ignored.
        The resume button must not react to that old press.
        made by: Mohammad Abu Aresh
        """
        self.menu.update(True)
        spot = center_of(self.menu.resume_box)
        with patch.object(pause_module, "pygame", fake_mouse(True, spot)):
            self.menu.update(False)
        self.assertTrue(self.menu.active)

    def test_main_menu_button_leaves_the_game(self) -> None:
        """Verify the main menu button returns to the main menu.
        Check the requested mode and that the pause is closed.
        made by: Mohammad Abu Aresh
        """
        self.menu.update(True)
        with patch.object(pause_module.Mod, "updatemod") as update_mod:
            self.click(center_of(self.menu.menu_box))
        update_mod.assert_called_once_with(pause_module.Mod.MAIN_MENU_SCREEN)
        self.assertFalse(self.menu.active)

    def test_contains_uses_a_half_open_rectangle(self) -> None:
        """Verify the hit test includes the top left and excludes the end.
        Check points on and just outside the rectangle edges.
        made by: Mohammad Abu Aresh
        """
        box = (10, 20, 100, 50)
        self.assertTrue(contains(box, (10, 20)))
        self.assertTrue(contains(box, (109, 69)))
        self.assertFalse(contains(box, (110, 20)))
        self.assertFalse(contains(box, (10, 70)))
        self.assertFalse(contains(box, (9, 20)))


if __name__ == "__main__":
    unittest.main()
