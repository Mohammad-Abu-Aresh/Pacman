import pygame


class GameEngine():
    def __init__(self) -> None:
        pass

    def run(self) -> None:
        pygame.init()
        screen = pygame.display.set_mode((400, 400))

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.fill((0, 0, 0))
            pygame.draw.rect(screen, (255, 255, 0), (180, 180, 40, 40))
            pygame.display.flip()

        pygame.quit()
