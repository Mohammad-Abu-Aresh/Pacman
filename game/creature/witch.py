import math
from .monster import Monster
from .abilities import SlowPotion
from .player import Player


class Witch(Monster):

    def __init__(
        self, spawn_point: tuple[int, int], is_hardcore: bool = False
    ) -> None:
        super().__init__(spawn_point, is_hardcore)
        self.potion_cooldown: float = 30.0  # cooldown in seconds
        self.radius_check: int = 5  # 5-block radius

    def throw_slow_potion(self, player: Player) -> None:
        """
        throws a slow potion if player is within radius
        witch is alive, and in hardcore mode
        """
        if not self.is_hardcore or not self.live:
            return

        distance = math.sqrt(
            (self.x - player.x) ** 2 + (self.y - player.y) ** 2
        )
        if distance <= self.radius_check:
            potion = SlowPotion((self.x, self.y), duration=5)
            potion.apply_effect(player)

    def move(self) -> None:
        pass

    def draw(self) -> None:
        pass

    def follow(self, player: Player) -> None:
        if self.live:
            self.target_point = (player.x, player.y)
        else:
            self.target_point = self.spawn_point
