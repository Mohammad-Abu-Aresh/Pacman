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
    screen = pygame.display.set_mode(
        (width, height)
    )

    @classmethod
    def _drow(cls, image: pygame.Surface, location: tuple[int, int]) -> None:
        Images.screen.blit(image, location)

    @classmethod
    def _update_size(cls, image_name: str, size: tuple[int, int]) -> None:
        # new_image_name = f"{image_name}_new"
        setattr(
            cls,
            image_name,

            pygame.transform.scale(
                getattr(cls, image_name),  # check if the str is in a cls
                size
            )  # chnenge size
        )
