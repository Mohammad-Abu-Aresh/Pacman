import sys
import pygame

state_variable: int = 1

# class Button:
#     def __init__(self, coordinates: tuple, text, font_size, position):
#         self.x = coordinates[0]
#         self.y = coordinates[1]
#         self.text = text
#         self.font_size = font_size
#         self.position = position
#     def draw(self, screen):
#         button_font = pygame.font.Font("font/minecraft.ttf", self.font_size)
#         button_text = button_font.render(self.text, False, "#000000")
#         screen.blit(
#             button_text,
#             (
#                 self.x - button_text.get_width() // 2,
#                 self.y - button_text.get_height() // 2,
#             ),
#         )


class GameEngine:
    def __init__(self) -> None:
        pass

    # def __start_screen(self, screen, width) -> None:
    #     bly_now = Button((width // 2, 200), "Bly Now", 30, (width // 2, 200))
    #     best_players = Button(
    #         (width // 2, 300), "Best Players", 30, (width // 2, 300)
    #     )
    #     exit_game = Button(
    #         (width // 2, 400), "Exit Game", 30, (width // 2, 400)
    #     )
    #     def draw_buttons():
    #         bly_now.draw(screen)
    #         best_players.draw(screen)
    #         exit_game.draw(screen)
    #     return draw_buttons

    def run(self) -> None:
        pygame.init()
        height = 600
        width = 800
        screen = pygame.display.set_mode(
            (width, height), pygame.RESIZABLE
        )
        pygame.display.set_caption("Pac-Man")
        clock = pygame.time.Clock()
        test_font = pygame.font.Font("font/minecraft.ttf", 50)
        # start_options = self.__start_screen(screen, width)
        title_game = test_font.render("Pac-Man", False, "#7B00FF")
        background = pygame.image.load("photos/kjf.png")

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            screen.blit(background, (0, 0))
            title_x = width // 2 - title_game.get_width() // 2
            screen.blit(title_game, (title_x, 20))
            # if state_variable == 1:
            #     start_options()
            pygame.display.update()
            clock.tick(60)

        def handle_events() -> None:
            pass

        def update_game_time() -> None:
            pass

        def toggle_cheat_mode() -> None:
            pass
