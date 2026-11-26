import pygame
from typing import cast
import os
import sys


def _resolve_path(path):
    if isinstance(path, str) and not os.path.isabs(path):
        candidates = [
            os.path.join(os.getcwd(), path),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), path),
        ]
        if hasattr(sys, "_MEIPASS"):
            candidates.insert(0, os.path.join(sys._MEIPASS, path))

        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate
        return candidates[0]
    return path


_original_load = pygame.image.load


def _patched_load(path, *args, **kwargs):
    return _original_load(_resolve_path(path), *args, **kwargs)


pygame.image.load = _patched_load


WALK_FRAME_NAMES = (
    "", "_walking", "_up", "_up_walking",
    "_r_stoped", "_r_front", "_r_back",
)


def _load_frames(folder: str, prefix: str) -> dict[str, pygame.Surface]:
    """
    Load every walking frame of one creature from its folder.
    Key each image by the suffix that follows the creature name.
    made by: Mohammad Abu Aresh
    """
    return {
        suffix: pygame.image.load(f"{folder}/{prefix}{suffix}.png")
        for suffix in WALK_FRAME_NAMES
    }


class Images:
    pygame.init()

    # drow = dic[int, col]
    screen_info = pygame.display.Info()
    width = screen_info.current_w
    height = screen_info.current_h
    # the main menu screen backgrond
    Home = pygame.image.load("photos/screens/main_creen.jpg")

    # background for each level
    level_1 = pygame.image.load("photos/background/background3.jpg")
    level_2 = pygame.image.load("photos/background/background4.jpg")
    level_3 = pygame.image.load("photos/background/background5.jpg")
    level_4 = pygame.image.load("photos/background/background6.jpg")
    level_5 = pygame.image.load("photos/background/background7.jpg")
    level_6 = pygame.image.load("photos/background/background8.jpg")
    level_7 = pygame.image.load("photos/background/background9.jpg")
    level_8 = pygame.image.load("photos/background/background10.jpg")
    level_9 = pygame.image.load("photos/background/background11.jpg")
    level_10 = pygame.image.load("photos/background/background12.jpg")
    victory_screen = pygame.image.load("photos/background/victory_screen.jpg")
    game_over_screen = pygame.image.load("photos/background/game_over.jpg")
    best_player_screen = pygame.image.load(
        "photos/background/best_players.jpg"
    )
    settings_screen = pygame.image.load("photos/background/settings.jpg")
    # wall image
    wall = pygame.image.load("photos/blocks/block-new.png")
    daimon = pygame.image.load("photos/blocks/jewels/daimon.png")
    netherite = pygame.image.load("photos/blocks/jewels/netherite_Ingot.png")

    player = pygame.image.load("photos/player/steve.png")
    player_heart = pygame.image.load("photos/player/heart/full_heart.png")
    pygame_heart_kell = pygame.image.load(
        "photos/player/heart/empty_heart.png"
        )
    zombie = pygame.image.load("photos/monsters/babyzombie/red.jpg")
    blue_ghost = pygame.image.load("photos/monsters/babyzombie/blue.png")
    witch = pygame.image.load("photos/monsters/babyzombie/red.jpg")
    skeleton = pygame.image.load("photos/monsters/babyzombie/red.jpg")
    enderman = pygame.image.load("photos/monsters/babyzombie/red.jpg")

    steve_frames = _load_frames("photos/player", "steve")
    zombie_frames = _load_frames("photos/monsters/zombie", "zombie")
    skeleton_frames = _load_frames("photos/monsters/skeleton", "skeleton")
    enderman_frames = _load_frames("photos/monsters/enderman", "enderman")
    witch_frames = _load_frames("photos/monsters/witch", "witch")

    # for mypy error handeling the _new image
    wall_new = wall

    player_new = player
    zombie_new = zombie
    witch_new = witch
    skeleton_new = skeleton
    enderman_new = enderman

    screen = pygame.display.set_mode(
        (width, height)
    )

    @classmethod
    def _drow(
        cls, image: pygame.Surface,
        location: tuple[int | float, int | float]
    ) -> None:
        """
        Blit the supplied image onto the shared display surface.
        Use the provided screen location without changing the image.
        made by: Mohammad Abu Aresh
        """
        Images.screen.blit(image, cast(tuple[int, int], location))

    @classmethod
    def _update_wall(cls, size: int) -> None:
        """
        Rescale the wall image so neighbouring walls touch seamlessly.
        Crop the transparent border and keep the old visible position.
        made by: Mohammad Abu Aresh
        """
        box = cls.wall.get_bounding_rect()
        width, height = cls.wall.get_size()
        scale_x = size * 2.1 / width
        scale_y = size * 1.85 / height
        block = pygame.transform.scale(
            cls.wall.subsurface(box),
            (size + 1, round(box.height * scale_y)),
        )
        canvas = pygame.Surface(
            (int(width * scale_x), int(height * scale_y)), pygame.SRCALPHA
        )
        canvas.blit(block, (round(box.x * scale_x), round(box.y * scale_y)))
        cls.wall_new = canvas

    @classmethod
    def _update_size(
        cls, image_name: str,
        size: tuple[int | float, int | float]
    ) -> None:
        """
        Scale a named original image to the requested dimensions.
        Store the scaled surface on the Images class using the _new
        suffix.
        made by: Mohammad Abu Aresh
        """
        setattr(
            cls,
            f"{image_name}_new",
            pygame.transform.scale(
                getattr(cls, image_name),
                size
            )
        )
