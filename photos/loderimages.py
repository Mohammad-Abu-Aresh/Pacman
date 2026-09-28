import pygame


class Images:
    pygame.init()
    screen_info = pygame.display.Info()
    width = screen_info.current_w
    height = screen_info.current_h
    # the main menu screen backgrond
    Home = pygame.image.load("photos/screens/main_creen.jpg")

    # background for each level
    level_1 = pygame.image.load("photos/background/background1.jpg")
    level_2 = pygame.image.load("photos/background/background2.jpg")

    # wall image
    wall = pygame.image.load("photos/blocks/test.png")
    screen = pygame.display.set_mode(
        (width, height)
    )