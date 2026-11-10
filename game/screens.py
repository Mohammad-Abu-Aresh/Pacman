from typing import Callable, Optional
import pygame
import json
from photos import Images


class Button:

    def __init__(
        self,
        coordinates: tuple[int, int],
        size: tuple[int, int],
        text: Optional[str] = None,
        font_size: int = 25,
        text_color: str | tuple[int, int, int] = "#000000",
    ) -> None:
        """
        Initialize button position, dimensions, label styling, and
        click state.
        Build the pygame rectangle used for hit testing and drawing.
        made by: Abdalghani Abtah
        update by: Mohammad Abu Aresh
        """
        self.x = coordinates[0]
        self.y = coordinates[1]
        self.text = text
        self.font_size = font_size
        self.text_color = text_color
        self.rect = pygame.Rect(
            self.x - size[0] // 2, self.y - size[1] // 2, size[0], size[1]
        )
        self.clicked = False

    def draw(self, screen: pygame.Surface) -> bool:
        """
        Draw the button label and detect a new mouse click inside
        its rectangle.
        Return True only for the click transition tracked by the
        clicked flag.
        made by: Abdalghani Abtah
        update by: Mohammad Abu Aresh
        """
        action = False
        button_font = pygame.font.Font(
            None, self.font_size
        )
        button_text = button_font.render(
            self.text if self.text is not None else "", False, self.text_color
        )
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if (
                pygame.mouse.get_pressed()[0]
                and not self.clicked
            ):
                self.clicked = True
                action = True
                print('CLICKED')
        else:
            self.clicked = False
        screen.blit(
            button_text,
            (
                self.x - button_text.get_width(),
                self.y - button_text.get_height(),
            ),
        )

        return action


class Screens:
    def __init__(
        self,
        screen: pygame.Surface,
        width: int,
        height: int
    ) -> None:
        """
        Store the screen surface and its dimensions for the UI
        screens.
        Initialize the text buffer used by the score-entry screen.
        made by: Abdalghani Abtah
        """
        self.screen = screen
        self.width = width
        self.height = height
        self.user_text = ''

    def main_menu_screen(
        self,
    ) -> Callable[[], dict[str, bool]]:
        """
        Create the main-menu buttons and prepare their drawing
        callback.
        Return a function that reports which menu action was
        clicked.
        made by: Abdalghani Abtah
        update by: Mohammad Abu Aresh
        """
        play_game = Button(
            (int(self.width * 0.21), int(self.height * 0.41)),
            (int(self.width * 0.22), int(self.height * 0.08))
        )
        minecraft_mode = Button(
            (int(self.width * 0.21), int(self.height * 0.51)),
            (int(self.width * 0.22), int(self.height * 0.08))
        )
        achievements = Button(
            (int(self.width * 0.21), int(self.height * 0.60)),
            (int(self.width * 0.22), int(self.height * 0.08))
        )
        settings = Button(
            (int(self.width * 0.21), int(self.height * 0.69)),
            (int(self.width * 0.22), int(self.height * 0.08))
        )
        quit_game = Button(
            (int(self.width * 0.21), int(self.height * 0.78)),
            (int(self.width * 0.22), int(self.height * 0.08))
        )

        def draw_buttons() -> dict[str, bool]:
            """
            Draw every main-menu button and collect their click results.
            Return the action mapping consumed by the game engine.
            made by: Abdalghani Abtah
            update by: Mohammad Abu Aresh
            """
            return {
                "play_game": play_game.draw(self.screen),
                "minecraft_mode": minecraft_mode.draw(self.screen),
                "top scores": achievements.draw(self.screen),
                "settings": settings.draw(self.screen),
                "quit_game": quit_game.draw(self.screen),
            }
        return draw_buttons

    def settings_screen(self) -> Callable[[], bool]:
        """
        Prepare the controls and instructions shown by the settings
        screen.
        Return a callback that draws the screen and reports an exit
        click.
        made by: Abdalghani Abtah
        """
        settings_image = pygame.transform.smoothscale(
            Images.settings_screen, (self.width, self.height)
        )
        exit_button = Button(
            coordinates=(self.width // 2, int(self.height * 0.9)),
            size=(220, 55),
            text=None,
            font_size=32,
            text_color=(240, 240, 240),
        )
        exit_label = pygame.font.Font(None, 32).render(
            "EXIT", True, (240, 240, 240)
        )
        exit_label_rect = exit_label.get_rect(
            center=(self.width // 2, int(self.height * 0.9))
        )

        def draw_settings() -> bool:
            """
            Render the instructions, divider, and exit button for the
            settings screen.
            Return the exit button click result to the game engine.
            made by: Abdalghani Abtah
            """
            self.screen.blit(settings_image, (0, 0))
            pygame.draw.rect(
                self.screen, (60, 80, 130),
                exit_button.rect, border_radius=10
            )
            pygame.draw.rect(
                self.screen, (160, 180, 230),
                exit_button.rect, width=2, border_radius=10
            )
            self.screen.blit(exit_label, exit_label_rect)
            return exit_button.draw(self.screen)
        return draw_settings

    def highscore_screen(
        self, highscore_file: str = "highscores.json"
    ) -> Callable[[], bool]:
        """
        Load, sort, and prepare the top score entries for display.
        Return a callback that renders the score list and its exit
        button.
        made by: Abdalghani Abtah
        update by: Mohammad Abu Aresh
        """

        font_item = pygame.font.Font(None, 36)
        bast_screen = pygame.transform.smoothscale(
            Images.best_player_screen, (self.width, self.height)
        )

        try:
            with open(highscore_file, "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []

        data = sorted(data, key=lambda x: x["score"], reverse=True)

        exit_button = Button(
            coordinates=(self.width // 2, int(self.height * 0.9)),
            size=(220, 55),
            text=None,
            font_size=32,
            text_color=(240, 240, 240),
        )

        exit_label = pygame.font.Font(None, 32).render(
            "EXIT", True, (240, 240, 240)
        )
        exit_label_rect = exit_label.get_rect(
            center=(self.width // 2, int(self.height * 0.9))
        )

        def draw_higscore() -> bool:
            """
            Render the title, up to ten score entries, and the exit
            button.
            Return the exit button click result to the game engine.
            made by: Abdalghani Abtah
            update by: Mohammad Abu Aresh
            """

            self.screen.blit(bast_screen, (0, 0))

            start_y = int(self.height * 0.50)

            for i, entry in enumerate(data[:10]):
                name = entry["name"]
                score = entry["score"]

                text_str = f"{i + 1}. {name} - {score} p"
                color = (
                    (255, 215, 0) if i == 0
                    else (240, 240, 240)
                )

                shadow_surf = font_item.render(text_str, True, (0, 0, 0))
                shadow_rect = shadow_surf.get_rect(
                    center=(
                        self.width // 2 + 2,
                        start_y + (i * 40) + 2
                    )
                )
                self.screen.blit(shadow_surf, shadow_rect)

                item_surf = font_item.render(
                    text_str, True, color
                )
                item_rect = item_surf.get_rect(
                    center=(
                        self.width // 2,
                        start_y + (i * 40)
                    )
                )
                self.screen.blit(item_surf, item_rect)

            pygame.draw.rect(
                self.screen,
                (60, 80, 130),
                exit_button.rect,
                border_radius=10,
            )
            pygame.draw.rect(
                self.screen,
                (160, 180, 230),
                exit_button.rect,
                width=2,
                border_radius=10,
            )

            self.screen.blit(exit_label, exit_label_rect)

            return exit_button.draw(self.screen)

        return draw_higscore

    def game_over_screen(
        self, final_score: int = 0, winner: bool = False
    ) -> Callable[[], None]:
        """
        Prepare the victory or game-over title, final score, and
        name input area.
        Return a callback that draws the prepared result screen.
        made by: Abdalghani Abtah
        """
        background = (
            Images.victory_screen if winner
            else Images.game_over_screen
        )
        background = pygame.transform.scale(
            background, (self.width, self.height)
        )

        font_text = pygame.font.Font(None, 36)
        score_surf = font_text.render(
            f"Final Score: {final_score}", True, (255, 255, 255)
        )
        score_rect = score_surf.get_rect(
            center=(self.width // 2, int(self.height * 0.4))
        )
        prompt_surf = font_text.render(
            "Enter your name (max 10 chars) & press ENTER:",
            True,
            (200, 200, 200)
        )
        prompt_rect = prompt_surf.get_rect(
            center=(self.width // 2, int(self.height * 0.5))
        )
        box_width = int(self.width * 0.3)
        box_height = 45
        input_rect = pygame.Rect(
            (self.width - box_width) // 2,
            int(self.height * 0.55),
            box_width,
            box_height
        )

        def draw_game_over() -> None:
            """
            Render the result title, final score, prompt, and name-entry
            box.
            Display the current user text within the input area.
            made by: Abdalghani Abtah
            """

            self.screen.blit(background, (0, 0))
            self.screen.blit(score_surf, score_rect)
            self.screen.blit(prompt_surf, prompt_rect)
            pygame.draw.rect(
                self.screen, (30, 30, 45), input_rect, border_radius=6
            )
            pygame.draw.rect(
                self.screen,
                (100, 150, 255),
                input_rect,
                2,
                border_radius=6
            )
            current_name = self.user_text[:10]
            name_surf = font_text.render(
                current_name, True, (255, 255, 255)
            )
            self.screen.blit(
                name_surf, (input_rect.x + 12, input_rect.y + 8)
            )

        return draw_game_over

    def addjson(self, name: str, score: int, file: str) -> None:
        """
        Load the score file, append the new result, and retain the
        top ten entries.
        Write through a temporary file before replacing the score
        file.
        made by: Abdalghani Abtah
        update by: Mohammad Abu Aresh
        """
        import os
        data = []
        if os.path.exists(file):
            try:
                with open(file, "r") as f:
                    content = f.read().strip()
                    if content:
                        data = json.loads(content)
            except (json.JSONDecodeError, OSError):
                data = []

        if not isinstance(data, list):
            data = []

        data.append({"name": name, "score": score})

        data.sort(key=lambda entry: entry.get("score", 0), reverse=True)
        data = data[:10]

        tmp_file = file + ".tmp"
        with open(tmp_file, "w") as f:
            json.dump(data, f, indent=4)
        os.replace(tmp_file, file)
