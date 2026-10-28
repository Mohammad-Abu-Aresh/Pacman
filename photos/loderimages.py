import pygame


class Images:
    pygame.init()

    # drow = dic[int, col]
    screen_info = pygame.display.Info()
    width = screen_info.current_w
    height = screen_info.current_h
    # the main menu screen backgrond
    Home = pygame.image.load("photos/screens/main_creen.jpg")

    # background for each level
    level_1 = pygame.image.load("photos/background/background1.jpg")
    level_2 = pygame.image.load("photos/background/background2.jpg")

    # wall image
    wall = pygame.image.load("photos/blocks/block.png")

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
    def _drow(cls, image: pygame.Surface, location: tuple[int, int]) -> None:
        Images.screen.blit(image, location)

    @classmethod
    def _update_size(
        cls, image_name: str,
        size: tuple[int | float, int | float]
    ) -> None:
        setattr(
            cls,
            f"{image_name}_new",
            pygame.transform.scale(
                getattr(cls, image_name),
                size
            )
        )
