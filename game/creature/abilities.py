import math
from .player import Direction, Player
from ..block import Block, Mape
from abc import ABC, abstractmethod
import pygame


# ===============================================
# hardcore objects (only used in hardcore mode)
# ===============================================

class Abilities(ABC):
    def __init__(self) -> None:
        """
        Initialize the abstract ability base class.
        The base currently stores no shared ability state.
        made by: Mohammad Abu Aresh
        """
        pass

    @abstractmethod
    def move(self) -> None:
        """
        Declare the movement interface required by concrete
        abilities.
        Subclasses provide the actual movement behavior.
        made by: Mohammad Abu Aresh
        """
        pass

    @abstractmethod
    def draw(self, image: pygame.Surface) -> None:
        """
        Declare the drawing interface for ability visuals.
        Concrete abilities provide their own rendering behavior.
        made by: Mohammad Abu Aresh
        """
        pass


class Arrow(Abilities):
    BASE_SPEED: float = 5.0
    WALL_MARGIN: float = 0.001

    def __init__(
        self, spawn_point: tuple[float, float],
        direction: tuple[int, int], speed: int = 300
    ) -> None:
        """
        Store the arrow spawn coordinates, direction, and movement
        speed.
        Use the supplied speed or the default projectile speed.
        made by: Mohammad Abu Aresh
        """
        self.x: float = float(round(spawn_point[0]))
        self.y: float = float(round(spawn_point[1]))
        self.direction: tuple[int, int] = direction
        self.speed: int = speed  # 300% of player speed
        self.active: bool = direction != Direction.none
        self.hit_player: bool = False
        self.swept_cells: list[tuple[int, int]] = [self.cell()]
        self.image: pygame.Surface = self._build_image()

    def _build_image(self) -> pygame.Surface:
        length = max(Block.size // 2, 4)
        thickness = max(Block.size // 8, 2)
        image = pygame.Surface((length, thickness), pygame.SRCALPHA)
        image.fill((120, 85, 40))
        tip = pygame.Rect(length - thickness, 0, thickness, thickness)
        pygame.draw.rect(image, (190, 190, 190), tip)
        angles = {
            Direction.right: 0, Direction.up: 90,
            Direction.left: 180, Direction.down: 270,
        }
        return pygame.transform.rotate(image, angles.get(self.direction, 0))

    def get_render_rect(self, mape: Mape) -> pygame.Rect:
        px = mape.origin_x + (self.x + 1.0) * Block.size
        py = mape.origin_y + (self.y + 0.8) * Block.size
        return self.image.get_rect(center=(int(px), int(py)))

    @staticmethod
    def _to_cell(value: float) -> int:
        return math.floor(value + 0.5)

    def cell(self) -> tuple[int, int]:
        return self._to_cell(self.x), self._to_cell(self.y)

    def hits(self, cell: tuple[int, int]) -> bool:
        return cell in self.swept_cells

    @staticmethod
    def _is_blocked(grid: list[list[bool]], x: int, y: int) -> bool:
        return not (
            0 <= y < len(grid) and 0 <= x < len(grid[y])
        ) or grid[y][x]

    def move(
        self,
        grid: list[list[bool]] | None = None,
        delta_time: float = 0.0,
    ) -> None:
        """
        Provide the movement hook for an Arrow instance.
        No projectile movement is implemented in this method yet.
        made by: Mohammad Abu Aresh
        """
        self.swept_cells = [self.cell()]
        if grid is None or not self.active:
            return
        step = self.direction[0] + self.direction[1]
        along_x = self.direction[0] != 0
        position = self.x if along_x else self.y
        lane = self.cell()[1] if along_x else self.cell()[0]
        distance = self.BASE_SPEED * self.speed / 100.0 * max(delta_time, 0.0)
        target = position + step * distance
        first = self._to_cell(position) + step
        last = self._to_cell(target) + step
        for index in range(first, last, step):
            x, y = (index, lane) if along_x else (lane, index)
            if self._is_blocked(grid, x, y):
                self.active = False
                stop = index - step * (0.5 + self.WALL_MARGIN)
                target = stop if (stop - position) * step > 0 else position
                break
            self.swept_cells.append((x, y))
        if along_x:
            self.x = target
        else:
            self.y = target

    def draw(self, image: pygame.Surface) -> None:
        """
        Provide the rendering hook for an Arrow instance.
        No arrow image is drawn by the current implementation.
        made by: Mohammad Abu Aresh
        """
        pass


class EnderPearl(Abilities):
    def __init__(self, target_point: tuple[int, int]) -> None:
        """
        Store the destination coordinates for an EnderPearl ability.
        The values are retained for the teleport action that uses
        the pearl.
        made by: Mohammad Abu Aresh
        """
        self.target_x: int = target_point[0]
        self.target_y: int = target_point[1]

    def move(self) -> None:
        """
        Provide the movement hook for an EnderPearl instance.
        The current implementation does not update the pearl
        position.
        made by: Mohammad Abu Aresh
        """
        pass

    def draw(self, image: pygame.Surface) -> None:
        """
        Provide the rendering hook for an EnderPearl instance.
        The current implementation does not draw a pearl image.
        made by: Mohammad Abu Aresh
        """
        pass


class SlowPotion(Abilities):
    def __init__(
            self, position: tuple[float, float], duration: int = 5
            ) -> None:
        """
        Store the potion position and the duration of its effect.
        The duration is later passed to the player speed update
        method.
        made by: Mohammad Abu Aresh
        """
        self.x: float = position[0]
        self.y: float = position[1]
        self.duration: int = duration  # slowdown duration in seconds

    def apply_effect(self, player: Player) -> None:
        """
        Request a reduced player speed for the configured duration.
        The player object handles how the speed update is stored.
        made by: Mohammad Abu Aresh
        """
        player.update_speed(35, self.duration)  # slow down the player

    def move(self) -> None:
        """
        Provide the movement hook for a SlowPotion instance.
        No potion movement is implemented in this method yet.
        made by: Mohammad Abu Aresh
        """
        pass

    def draw(self, image: pygame.Surface) -> None:
        """
        Provide the rendering hook for a SlowPotion instance.
        No potion visual is drawn by the current implementation.
        made by: Mohammad Abu Aresh
        """
        pass
