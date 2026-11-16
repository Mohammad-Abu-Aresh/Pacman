import os
import unittest
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from game.block import Block  # noqa: E402
from game.creature import spawn_point as spawn_module  # noqa: E402
from game.creature.spawn_point import Diamond, Netherite  # noqa: E402


class CollectibleDrawTests(unittest.TestCase):
    def setUp(self) -> None:
        """Set the block size and a map origin for the drawing math.
        Restore the real block size after every test.
        made by: Mohammad Abu Aresh
        """
        self.old_size = Block.size
        Block.size = 40
        self.addCleanup(setattr, Block, "size", self.old_size)
        self.mape: Any = SimpleNamespace(origin_x=100, origin_y=50)

    def draw(self, gum: Any, times: int = 1) -> tuple[Any, Any]:
        """Draw a collectible with the image helpers replaced by mocks.
        Return the scale mock and the screen drawing mock.
        made by: Mohammad Abu Aresh
        """
        scale = MagicMock(return_value="scaled")
        fake_pygame = SimpleNamespace(
            transform=SimpleNamespace(scale=scale),
            Surface=lambda size: "empty",
        )
        fake_images = SimpleNamespace(_drow=MagicMock())
        with patch.object(spawn_module, "pygame", fake_pygame), patch.object(
            spawn_module, "Images", fake_images
        ):
            for _ in range(times):
                gum.draw(self.mape)
        return scale, fake_images._drow

    def make(self, kind: Any) -> Any:
        """Create a collectible of the given kind with a fake image.
        Use a mock screen and the default configuration.
        made by: Mohammad Abu Aresh
        """
        fake_pygame = SimpleNamespace(Surface=lambda size: "empty")
        fake_images = SimpleNamespace(daimon="d", netherite="n")
        with patch.object(spawn_module, "pygame", fake_pygame), patch.object(
            spawn_module, "Images", fake_images
        ):
            return kind(MagicMock(), {}, 2, 3)

    def test_cache_fields_exist_before_the_first_draw(self) -> None:
        """Verify the scaled image fields are declared on creation.
        They must exist so the first draw can compare the size.
        made by: Mohammad Abu Aresh
        """
        gum = self.make(Diamond)
        self.assertEqual(gum._scaled_size, (0, 0))
        self.assertTrue(hasattr(gum, "_scaled"))

    def test_diamond_is_scaled_once_and_drawn_every_frame(self) -> None:
        """Verify the image is rescaled only when the size changes.
        The drawing call still happens on every frame.
        made by: Mohammad Abu Aresh
        """
        scale, drow = self.draw(self.make(Diamond), 3)
        scale.assert_called_once_with("d", (20, 20))
        self.assertEqual(drow.call_count, 3)

    def test_diamond_position_follows_the_block_size(self) -> None:
        """Verify the diamond is centered from the grid position.
        Check the pixel position for column two and row three.
        made by: Mohammad Abu Aresh
        """
        scale, drow = self.draw(self.make(Diamond))
        drow.assert_called_once_with("scaled", (215, 205))

    def test_netherite_uses_its_own_image_and_shift(self) -> None:
        """Verify the super gum uses the netherite image.
        Check the larger shift used for its position.
        made by: Mohammad Abu Aresh
        """
        scale, drow = self.draw(self.make(Netherite))
        scale.assert_called_once_with("n", (20, 20))
        drow.assert_called_once_with("scaled", (220, 210))

    def test_size_change_rescales_the_image(self) -> None:
        """Verify a new block size triggers a new scale.
        Draw once, change the size and draw again.
        made by: Mohammad Abu Aresh
        """
        gum = self.make(Diamond)
        scale, _ = self.draw(gum)
        Block.size = 60
        scale2, _ = self.draw(gum)
        scale2.assert_called_once_with("d", (30, 30))

    def test_eaten_collectible_is_not_drawn(self) -> None:
        """Verify an eaten collectible draws nothing.
        Neither the scale nor the drawing call may run.
        made by: Mohammad Abu Aresh
        """
        gum = self.make(Diamond)
        gum.is_eaten = True
        scale, drow = self.draw(gum)
        scale.assert_not_called()
        drow.assert_not_called()


if __name__ == "__main__":
    unittest.main()
