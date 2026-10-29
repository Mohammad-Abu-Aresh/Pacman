from typing import Callable, Optional
import pygame
import json


class Button:

    def __init__(
        self,
        coordinates: tuple[int, int],
        size: tuple[int, int],
        text: Optional[str] = None,
        font_size: int = 25,
        text_color: str | tuple[int, int, int] = "#000000",
    ) -> None:
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
        self.screen = screen
        self.width = width
        self.height = height
        self.user_text = ''

    def main_menu_screen(
        self,
    ) -> Callable[[], dict[str, bool]]:
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
            return {
                "play_game": play_game.draw(self.screen),
                "minecraft_mode": minecraft_mode.draw(self.screen),
                "top scores": achievements.draw(self.screen),
                "settings": settings.draw(self.screen),
                "quit_game": quit_game.draw(self.screen),
            }
        return draw_buttons

    def settings_screen(self) -> Callable[[], bool]:
        font_title = pygame.font.Font(None, 50)
        font_text = pygame.font.Font(None, 32)

        title_surf = font_title.render("HOW TO PLAY", True, (255, 215, 0))
        title_rect = title_surf.get_rect(
            center=(self.width // 2, int(self.height * 0.12))
        )

        instructions = [
            "Up Arrow     →  Move Up",
            "Down Arrow   →  Move Down",
            "Left Arrow   →  Move Left",
            "Right Arrow  →  Move Right",
            "",
            "Eat all the dots to win the level.",
            "Avoid the ghosts!",
            "Eat a Power Pellet to chase ghosts.",
        ]
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
            self.screen.fill((15, 15, 25))
            self.screen.blit(title_surf, title_rect)
            pygame.draw.line(
                self.screen, (255, 215, 0),
                (self.width // 2 - 160, title_rect.bottom + 10),
                (self.width // 2 + 160, title_rect.bottom + 10),
                2,
            )
            start_y = int(self.height * 0.28)
            for i, line in enumerate(instructions):
                if line == "":
                    continue
                surf = font_text.render(line, True, (220, 220, 220))
                rect = surf.get_rect(
                    center=(self.width // 2, start_y + i * 40)
                )
                self.screen.blit(surf, rect)
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
        aabtah
        اخذ المعلومات من ملف json
        رابط الفيديو : <https://www.youtube.com/watch?v=__mZO-53PPM&t=799s>
        """
        font_title = pygame.font.Font(None, 50)
        font_item = pygame.font.Font(None, 36)

        title_surf = font_title.render(
            "TOP 10 SCORES", True, (255, 215, 0)
        )
        title_rect = title_surf.get_rect(
            center=(self.width // 2, int(self.height * 0.15))
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
            self.screen.fill((15, 18, 30))
            self.screen.blit(title_surf, title_rect)

            pygame.draw.line(
                self.screen,
                (255, 215, 0),
                (self.width // 2 - 160, title_rect.bottom + 10),
                (self.width // 2 + 160, title_rect.bottom + 10),
                2,
            )

            start_y = int(self.height * 0.28)

            for i, entry in enumerate(data[:10]):
                name = entry["name"]
                score = entry["score"]

                text_str = f"{i + 1}. {name} - {score} p"
                color = (
                    (255, 215, 0) if i == 0
                    else (240, 240, 240)
                )

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
        font_title = pygame.font.Font(None, 60)
        font_text = pygame.font.Font(None, 36)
        status_text = "VICTORY!" if winner else "GAME OVER"
        title_color = (0, 255, 0) if winner else (255, 0, 0)
        title_surf = font_title.render(status_text, True, title_color)
        title_rect = title_surf.get_rect(
            center=(self.width // 2, int(self.height * 0.3))
        )
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
            self.screen.fill((0, 0, 0))
            self.screen.blit(title_surf, title_rect)
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
