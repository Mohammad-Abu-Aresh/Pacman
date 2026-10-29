import pygame
from game.creature.player import movement, Direction
from .creature import (
    Creature,
    Control_creature,
    Diamond,
    Netherite,
)
from photos.loderimages import Images
from typing import Dict, Any
from .block import Mape
from .game_modes import Mod
from .level_builder import build_level
from .game_renderer import (
    draw_game as render_game,
    draw_heart as render_heart,
    draw_hud as render_hud,
    draw_maze as render_maze,
    draw_score as render_score,
    draw_timer as render_timer,
)


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
            maze_map=self.maze_map, lives=self.lives,
            super_timer=15
        )
        self.mobs: tuple[Creature, ...] = (
                self.player_creature.player,
                self.player_creature.BabyZombie,
                self.player_creature.Skeleton,
                self.player_creature.Enderman,
                self.player_creature.witch,
                )
        self.wait_timer: float = 2.0
        self.pending_action: str | None = None

    def load_level(self) -> None:
        build_level(self)

    def next_level(self) -> None:
        if self.current_level <= self.max_levels:
            self.current_level += 1
        else:
            self.current_level = 1
        if self.current_level > self.config["max_levels"]:
            Mod.updatemod(Mod.VICTORY_SCREEN)
            return
        self.load_level()
        movement.traffic_update(Direction.none)
        self.player_creature.refresh(self.maze_map)
        self.wait_timer = 1.0
        self.pending_action = "frozen"

    def update(self, time: float, cheating: bool = False) -> None:
        if self.wait_timer > 0:
            self.wait_timer -= time
            if self.wait_timer <= 0:
                self.wait_timer = 0
                self.pending_action = None
            return

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

        if self.player_creature.check_collision(
            self.config.get("points_per_ghost", 200)
        ):
            mob.follow(self.player_creature.player, grid)
            mob.move(grid)

        if not cheating and self.player_creature.check_collision():
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
        self.wait_timer = 1.0
        self.pending_action = "frozen"

    def draw(self) -> None:
        render_game(self)

    def _draw_maze(
            self,
            origin_x: int,
            origin_y: int
            ) -> None:
        render_maze(self, origin_x, origin_y)

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
        render_hud(self)

    def _draw_timer(self, x: int, y: int) -> None:
        render_timer(self, x, y)

    def _draw_score(self, x: int, y: int) -> None:
        render_score(self, x, y)

    def _heart(self, x: int, y: int) -> None:
        render_heart(self, x, y)

    def points(self) -> int:
        return self.player_creature.player.score
