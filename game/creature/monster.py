
from abc import ABC, abstractmethod
from .bfs import PathFinder
from .creature import Creature
from .player import Direction, Player
from .ghost_modes import MODE_SCHEDULE as GHOST_MODE_SCHEDULE
from .ghost_state import (
    activate_monster_frightened,
    set_monster_frightened_visual,
    reactivate_monster_at_home,
    reset_monster_ai,
    step_towards,
    update_monster_mode,
)


class Monster(Creature, ABC):
    MODE_SCHEDULE = GHOST_MODE_SCHEDULE

    def __init__(
        self, spawn_point: tuple[int, int],
        is_hardcore: bool = False
    ) -> None:
        """
        Initialize spawn, position, target, movement, and life-state
        fields.
        Prepare the first Scatter mode and the frightened-state
        timer.
        made by: Mohammad Abu Aresh
        """
        self.spawn_point: tuple[int, int] = spawn_point
        self.x = float(spawn_point[0])
        self.y = float(spawn_point[1])
        self.locaion: tuple[float, float] = (self.x, self.y)
        self.target_point: tuple[int, int] | None = None
        self.next_point: tuple[int, int] | None = None
        self.live: bool = True
        self.speed: int = 65
        self.is_following: bool = True
        self.is_hardcore: bool = is_hardcore
        self.movement_direction: tuple[int, int] = Direction.none
        self.mode_index = 0
        self.mode, self.mode_timer = self.MODE_SCHEDULE[0]
        self.reverse_pending = False
        self.frightened = False
        self.frightened_timer = 0.0

    @abstractmethod
    def follow(self, player: Player) -> None:
        """
        Declare the target-selection hook implemented by each
        monster type.
        Subclasses choose their own behavior for the supplied
        player.
        made by: Mohammad Abu Aresh
        """
        pass

    @staticmethod
    def _step_towards(
        current: float,
        target: float,
        distance: float,
    ) -> float:
        """
        Delegate one bounded scalar movement step to the shared
        helper.
        Return a value that approaches the target without
        overshooting it.
        made by: Mohammad Abu Aresh
        """
        return step_towards(current, target, distance)

    def reset_ai(self) -> None:
        """
        Delegate restoration of the monster AI state to the state
        helpers.
        Reset its mode, target, movement direction, and frightened
        fields.
        made by: Mohammad Abu Aresh
        """
        reset_monster_ai(self)

    def activate_frightened(self, duration: float) -> None:
        """
        Delegate frightened activation for this monster.
        The state helper handles the timer, visual, and reversal
        request.
        made by: Mohammad Abu Aresh
        """
        activate_monster_frightened(self, duration)

    def _update_mode(self, delta_time: float) -> None:
        """
        Update this monster current Scatter or Chase mode timer.
        Mode transitions are handled by the shared ghost-state
        helper.
        made by: Mohammad Abu Aresh
        """
        update_monster_mode(self, delta_time)

    def _choose_next_point(
        self,
        grid: list[list[bool]],
        current_cell: tuple[int, int],
        player_cell: tuple[int, int] | None = None,
    ) -> tuple[int, int] | None:
        """
        Choose the next legal grid cell according to the monster
        state.
        Use pathfinding for dead return, frightened escape, or
        normal targeting.
        made by: Mohammad Abu Aresh
        """
        if self.target_point is None:
            return None
        if not self.live:
            return PathFinder.next_step(grid, current_cell, self.target_point)
        if self.frightened and player_cell is not None:
            return PathFinder.next_step_away(
                grid, current_cell, player_cell
            )
        return PathFinder.next_step_towards(
            grid,
            current_cell,
            self.target_point,
            self.movement_direction,
            self.reverse_pending,
        )

    def move(
        self,
        grid: list[list[bool]] | None = None,
        delta_time: float = 1 / 60,
        player_cell: tuple[int, int] | None = None,
    ) -> None:
        """
        Update monster state and move it incrementally toward its
        next cell.
        Validate the stored step, choose a legal route step, and
        update its position.
        made by: Mohammad Abu Aresh
        """
        if grid is None:
            return

        delta_time = max(delta_time, 0.0)
        if self.frightened:
            self.frightened_timer -= delta_time
            if self.frightened_timer <= 0:
                self.frightened = False
                self.frightened_timer = 0.0
                set_monster_frightened_visual(self, False)
                self.target_point = None
        else:
            self._update_mode(delta_time)

        delta_time = min(delta_time, 0.05)
        current_cell = (round(self.x), round(self.y))
        if reactivate_monster_at_home(self):
            return
        if self.target_point is None:
            return

        if self.next_point is not None:
            next_x, next_y = self.next_point

            distance = (
                abs(next_x - current_cell[0])
                + abs(next_y - current_cell[1])
            )

            in_bounds = (
                0 <= next_y < len(grid)
                and 0 <= next_x < len(grid[next_y])
            )

            if (
                distance > 1
                or not in_bounds
                or grid[next_y][next_x]
            ):
                self.next_point = None

        if self.next_point is None:
            self.next_point = self._choose_next_point(
                grid, current_cell, player_cell
            )
            if self.next_point is not None:
                self.movement_direction = (
                    self.next_point[0] - current_cell[0],
                    self.next_point[1] - current_cell[1],
                )
                self.reverse_pending = False

        if self.next_point is None:
            return

        next_x, next_y = self.next_point
        step = 5.0 * (self.speed / 100.0) * delta_time
        if self.frightened:
            step *= 0.5

        if next_y == self.y:
            self.x = self._step_towards(
                self.x, next_x, step
            )
        else:
            self.y = self._step_towards(
                self.y, next_y, step
            )

        self.locaion = (self.x, self.y)
        if (self.x, self.y) == self.next_point:
            self.next_point = None

    def set_hardcore_mode(self, enabled: bool) -> None:
        """
        Store whether hardcore mode is enabled for this monster.
        Concrete monster types may extend this method with mode-
        specific behavior.
        made by: Mohammad Abu Aresh
        """
        self.is_hardcore = enabled

    def die(self) -> None:
        """
        Mark the monster as inactive and stop its following
        behavior.
        Set its return target to spawn and clear the stored next
        cell.
        made by: Mohammad Abu Aresh
        """
        self.live = False
        self.is_following = False
        self.target_point = self.spawn_point
        self.next_point = None
