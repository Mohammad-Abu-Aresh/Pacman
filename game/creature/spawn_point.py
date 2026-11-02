from abc import ABC, abstractmethod
import pygame
from game.block import Block
from game.block import Mape


class pacgum(ABC):
    def __init__(
            self, screen: pygame.Surface, config: dict, x: int, y: int
            ) -> None:
        """
        Store the drawing surface, configuration, and collectible
        grid position.
        Initialize the collectible as not yet eaten.
        made by: Abdalghani Abtah
        update by: Mohammad Abu Aresh
        """
        self.screen = screen
        self.config = config
        self.x = x
        self.y = y
        self.is_eaten = False

    @abstractmethod
    def draw(self, mape: Mape) -> None:
        """
        Declare the drawing interface for concrete collectible
        types.
        Each collectible subclass defines its own shape and
        appearance.
        made by: Abdalghani Abtah
        """
        pass

    def eaten(self) -> None:
        """
        Mark the collectible as eaten.
        Drawing methods use this flag to skip consumed collectibles.
        made by: Abdalghani Abtah
        update by: Mohammad Abu Aresh
        """
        self.is_eaten = True

    def get_position(self) -> tuple[int, int]:
        """
        Return the collectible position as an x and y grid-
        coordinate tuple.
        The stored integer coordinates are returned without
        conversion.
        made by: Abdalghani Abtah
        update by: Mohammad Abu Aresh
        """
        return self.x, self.y


class Diamond(pacgum):
    def __init__(
            self, screen: pygame.Surface,
            config: dict, x: int, y: int
            ) -> None:
        """
        Initialize the base collectible data and standard pellet
        score.
        Read the score value from configuration or use its default.
        made by: Abdalghani Abtah
        update by: Mohammad Abu Aresh
        """
        super().__init__(screen, config, x, y)
        self.points = config.get("points_per_pacgum", 10)

    def draw(self, mape: Mape) -> None:
        """
        Draw an uneaten standard pellet at its mapped maze
        coordinates.
        Skip rendering after the collectible has been consumed.
        made by: Abdalghani Abtah
        update by: Mohammad Abu Aresh
        """
        if self.is_eaten:
            return

        shift_x = 15
        shift_y = 15

        px = int(
            mape.origin_x + (
                self.x * Block.size
                ) + (Block.size // 2) + shift_x
            )
        py = int(
            mape.origin_y + (
                self.y * Block.size
                ) + (Block.size // 2) + shift_y
                )

        pygame.draw.circle(
            self.screen, (255, 255, 255), (px, py), Block.size // 6
            )


class Netherite(pacgum):
    def __init__(
            self, screen: pygame.Surface, config: dict, x: int, y: int
            ) -> None:
        """
        Initialize the base collectible data and power pellet score.
        Read the score value from configuration or use its default.
        made by: Abdalghani Abtah
        update by: Mohammad Abu Aresh
        """
        super().__init__(screen, config, x, y)
        self.points = config.get("points_per_super_pacgum", 50)

    def draw(self, mape: Mape) -> None:
        """
        Draw an uneaten power pellet at its mapped maze coordinates.
        Use the larger orange circle and skip rendering after it is
        eaten.
        made by: Abdalghani Abtah
        update by: Mohammad Abu Aresh
        """
        if self.is_eaten:
            return
        shift_x = 20
        shift_y = 20
        px = int(
            mape.origin_x + (
                self.x * Block.size
                ) + (Block.size // 2) + shift_x
                )
        py = int(
            mape.origin_y + (
                self.y * Block.size
                ) + (Block.size // 2) + shift_y
                )
        pygame.draw.circle(
            self.screen, (255, 165, 0), (px, py), Block.size // 3
            )
