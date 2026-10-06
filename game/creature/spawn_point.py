from abc import ABC, abstractmethod
import pygame
from game.block import Block
from game.block import Mape


class pacgum(ABC):
    def __init__(self,screen: pygame.Surface, config: dict, x: int, y: int) -> None:
        self.screen = screen
        self.config = config
        self.x = x
        self.y = y
        self.is_eaten = False

    @abstractmethod
    def draw(self, mape: Mape) -> None:
        pass

    def eaten(self):
        self.is_eaten = True
    
    def get_position(self):
        return  self.x, self.y

class Diamond(pacgum):
    def __init__(self, screen: pygame.Surface, config: dict, x: int, y: int) -> None:
        super().__init__(screen, config, x, y)
        self.points = config.get("points_per_pacgum", 100)

    def draw(self, mape: Mape) -> None:
        if self.is_eaten:
            return
        
        shift_x = 15  
        shift_y = 15  

        px = int(mape.origin_x + (self.x * Block.size) + (Block.size // 2) + shift_x)
        py = int(mape.origin_y + (self.y * Block.size) + (Block.size // 2) + shift_y)
        
        pygame.draw.circle(self.screen, (255, 255, 255), (px, py), Block.size // 6)


class Netherite(pacgum):
    def __init__(self, screen: pygame.Surface, config: dict, x: int, y: int) -> None:
        super().__init__(screen, config, x, y)
        self.points = config.get("points_per_super_pacgum", 500)

    def draw(self, mape: Mape) -> None:
        if self.is_eaten:
            return
        shift_x = 20
        shift_y = 20
        px = int(mape.origin_x + (self.x * Block.size) + (Block.size // 2) + shift_x)
        py = int(mape.origin_y + (self.y * Block.size) + (Block.size // 2) + shift_y)
        pygame.draw.circle(self.screen, (255, 165, 0), (px, py), Block.size // 3)
