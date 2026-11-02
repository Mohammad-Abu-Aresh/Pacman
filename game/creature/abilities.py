from .player import Player
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

    def __init__(
        self, spawn_point: tuple[float, float],
        direction: int, speed: int = 300
    ) -> None:
        """
        Store the arrow spawn coordinates, direction, and movement
        speed.
        Use the supplied speed or the default projectile speed.
        made by: Mohammad Abu Aresh
        """
        self.x: float = spawn_point[0]
        self.y: float = spawn_point[1]
        self.direction: int = direction
        self.speed: int = speed  # 300% of player speed

    def move(self) -> None:
        """
        Provide the movement hook for an Arrow instance.
        No projectile movement is implemented in this method yet.
        made by: Mohammad Abu Aresh
        """
        pass

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
