import pygame
import random
from game.creature.player import movement, Direction
from .creature import (
    Creature,
    Control_creature,
    Diamond,
    Netherite,
)
from photos.loderimages import Images
from typing import Dict, Any
from mazegenerator import MazeGenerator
from .block import Mape, Block
from .game_modes import Mod


class GameSystem:
    maze_map: Mape

    backphoto: dict[int, Any] = {
        1: Images.level_1,
        2: Images.level_2,
        }

    def __init__(
            self, config: Dict[str, Any],
            hardcore_mode: bool = False,
            cheating: bool = False
            ) -> None:
        self.num = 0
        self.config = config
        self.current_level: int = 1
        self.max_levels: int = config["max_levels"]
        self.lives: int = self.config.get("lives", 3)
        self.level_max_time: int = self.config.get("level_max_time", 90)
        self.hardcore_mode = hardcore_mode
        self.cheating = cheating
        self.row = 7
        self.column = 7
        self.load_level()
        self.time_left: float = float(self.level_max_time)
        pygame.font.init()
        self.font = pygame.font.SysFont(None, 36)
        self.player_creature = Control_creature(
            maze_map=self.maze_map,
            lives=self.lives,
            super_timer=15
            )
        self.mobs: tuple[Creature, ...] = (
                self.player_creature.player,
                self.player_creature.BabyZombie,
                self.player_creature.Skeleton,
                self.player_creature.Enderman,
                self.player_creature.witch,
                )

    def load_level(self) -> None:
        if self.current_level == 1:
            self.num += 1
            self.seed = self.config.get("seed", 42)
            self.row = 11
            self.column = 7
            self.backimage = self.backphoto[self.current_level + 1]
            self.background = pygame.transform.scale(
                self.backimage,
                (
                    Images.width,
                    Images.height,
                ),
            )
        else:
            self.num += 1
            self.seed = random.randint(1, 2004)
            if (
                self.num == 3 or self.num == 6 or
                self.num == 9 or self.num == 12
            ):
                self.row += 2
                self.column += 1
            else:
                self.player_creature.player._super_timer -= 2
        maze = MazeGenerator(
            size=(self.row, self.column), seed=self.seed
            )
        self.maze_map = Mape(maze)
        Images._update_size(
            "wall", size=(Block.size * 2.1, Block.size * 1.85)
            )
        self.time_left = self.level_max_time
        movement.traffic_update(Direction.none)

        self.collectibles: list[Diamond | Netherite] = []
        height = len(self.maze_map.every_cell)
        max_y = height - 1
        max_x = len(self.maze_map.every_cell[0]) - 1 if height > 0 else 0
        corners = {
            (1, 1),
            (max_x - 1, 1),
            (1, max_y - 1),
            (max_x - 1, max_y - 1)
            }
        for y, row in enumerate(self.maze_map.coordination_42):
            for x, cell in enumerate(row):
                if not cell:
                    if (x, y) in corners:
                        self.collectibles.append(
                            Netherite(Images.screen, self.config, x, y)
                            )
                    else:
                        self.collectibles.append(
                            Diamond(Images.screen, self.config, x, y)
                            )

    def next_level(self) -> None:
        if self.current_level <= self.max_levels:
            self.current_level += 1
        else:
            self.current_level = 1
        if self.current_level > self.config["max_levels"]:
            Mod.updatemod(Mod.VICTORY_SCREEN)
        self.load_level()
        movement.traffic_update(Direction.none)
        self.player_creature.refresh(self.maze_map)

    def update(self, time: float, cheating: bool = False) -> None:
        if self.time_left > 0:
            self.time_left -= time
        else:
            Mod.updatemod(Mod.GAME_OVER_SCREEN)
        keys = pygame.key.get_pressed()
        self.player_creature.update_frightened(time)
        self.player_creature.player.change_diric()
        self.player_creature.player.move()
        grid = self.maze_map.every_cell

        for mob in (
            self.player_creature.BabyZombie,
            self.player_creature.Skeleton,
            self.player_creature.Enderman,
            self.player_creature.witch,
        ):
            mob.follow(
                self.player_creature.player, grid
            )
            mob.move(
                grid,
                time,
                (
                    round(self.player_creature.player.x),
                    round(self.player_creature.player.y),
                ),
            )

        if self.player_creature.check_collision():
            self._handle_player_death()
            return

        self._eat_pacgums()
        if keys[pygame.K_n] and cheating:
            self.next_level()
        if keys[pygame.K_ESCAPE]:
            Mod.updatemod(Mod.MAIN_MENU_SCREEN)

    def _handle_player_death(self) -> None:
        player = self.player_creature.player
        player.respawn()
        self.lives = player._lives

        if self.lives <= 0:
            Mod.updatemod(Mod.GAME_OVER_SCREEN)
            return

        self.player_creature.reset_mobs()

    def draw(self) -> None:

        self._draw_maze(
            self.maze_map.origin_x,
            self.maze_map.origin_y
            )
        for item in self.collectibles:
            item.draw(self.maze_map)
        for mob in sorted(
            self.mobs,
            key=lambda mob: int(mob.y + 0.5)
        ):
            mob.draw(self.maze_map)
        self._draw_hud()

    def _draw_maze(
            self,
            origin_x: int,
            origin_y: int
            ) -> None:
        maze_bool = self.maze_map.every_cell

        cell_size = Block.size
        for item in self.collectibles:
            item.draw(self.maze_map)

        Images.screen.blit(self.background, (0, 0))
        for y, row in enumerate(maze_bool):
            for x, cell in enumerate(row):
                location_x = origin_x + (x * cell_size)
                location_y = origin_y + (y * cell_size)
                if cell:
                    Images._drow(
                        Images.wall_new,
                        location=(location_x, location_y)
                        )
                else:
                    continue

    def _eat_pacgums(self) -> None:
        player = self.player_creature.player

        player_x = int(player.x + 0.5)
        player_y = int(player.y + 0.5)

        for item in self.collectibles:
            if item.is_eaten:
                continue

            if item.x == player_x and item.y == player_y:
                item.eaten()
                player.eat(item.points)
                if isinstance(item, Netherite):
                    self.player_creature.activate_frightened(
                        max(float(player._super_timer), 1.0)
                    )
        if self.collectibles and all(
            item.is_eaten for item in self.collectibles
        ):
            self.next_level()

    def _draw_hud(self) -> None:
        panel_x = 1480
        panel_y = 100
        spacing_y = 50
        self._draw_timer(panel_x, panel_y)
        self._draw_score(panel_x, panel_y + spacing_y)
        self._heart(panel_x, panel_y + (spacing_y * 2))

    def _draw_timer(self, x: int, y: int) -> None:
        shadow_surface = self.font.render(
            f"Time: {int(self.time_left)}", True, (0, 0, 0)
            )
        Images.screen.blit(
            shadow_surface, (x + 2, y + 2)
            )
        text_surface = self.font.render(
            f"Time: {int(self.time_left)}", True, (255, 255, 255)
            )
        Images.screen.blit(
            text_surface, (x, y)
            )

    def _draw_score(self, x: int, y: int) -> None:
        score = self.player_creature.player.score
        shadow_surface = self.font.render(
            f"Score: {score}", True, (0, 0, 0)
            )
        Images.screen.blit(
            shadow_surface, (x + 2, y + 2)
            )
        text_surface = self.font.render(
            f"Score: {score}", True, (255, 255, 255)
            )
        Images.screen.blit(text_surface, (x, y))

    def _heart(self, x: int, y: int) -> None:
        lives = self.player_creature.player._lives
        heart_alive = Images.player_heart
        heart_dead = Images.pygame_heart_kell

        spacing = 45

        if lives <= 3:
            for i in range(3):
                heart_x = x + i * spacing
                if i < lives:
                    Images._drow(heart_alive, (heart_x, y))
                else:
                    Images._drow(heart_dead, (heart_x, y))
        else:
            Images._drow(heart_alive, (x, y))
            font = pygame.font.SysFont("Arial", 30, bold=True)
            shadow_surface = font.render(f"x {lives}", True, (0, 0, 0))
            Images.screen.blit(shadow_surface, (x + 47, y + 7))
            text_surface = font.render(f"x {lives}", True, (255, 255, 255))
            Images.screen.blit(text_surface, (x + 45, y + 5))

    def points(self) -> int:
        return self.player_creature.player.score
