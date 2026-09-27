from .abilities import EnderPearl
from .monster import Monster
from .player import Player
import random


class Enderman(Monster):

    def __init__(
        self, spawn_point: tuple[int, int], is_hardcore: bool = False
    ) -> None:
        super().__init__(spawn_point, is_hardcore)
        self.teleport_cooldown: float = 20.0  # every 20 seconds
        self.current_pearl: EnderPearl | None = None

    def throw_pearl_and_teleport(self, maze_bounds: tuple[int, int]) -> None:
        """
        teleports the enderman using an enderpearl
        if alive and in hardcore mode
        """
        if not self.is_hardcore or not self.live:
            return

        rand_x = random.randint(0, maze_bounds[0])
        rand_y = random.randint(0, maze_bounds[1])

        self.current_pearl = EnderPearl((rand_x, rand_y))
        self.x = rand_x
        self.y = rand_y

    def move(self) -> None:
        pass

    def draw(self) -> None:
        pass

    def follow(self, player: Player) -> None:
        if self.live:
            self.target_point = (player.x, player.y)
        else:
            self.target_point = self.spawn_point
