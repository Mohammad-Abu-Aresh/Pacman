from .monster import Monster
from .player import Player


class BabyZombie(Monster):

    def __init__(
        self, spawn_point: tuple[int, int], is_hardcore: bool = False
    ) -> None:
        super().__init__(spawn_point, is_hardcore)
        if self.is_hardcore and self.live:
            self.speed = 110

    def set_hardcore_mode(self, enabled: bool) -> None:
        super().set_hardcore_mode(enabled)
        if self.live:
            self.speed = 110 if enabled else 65

    def move(self) -> None:
        pass

    def draw(self) -> None:
        pass

    def follow(self, player: Player) -> None:
        if self.live:
            self.target_point = (player.x, player.y)
        else:
            self.target_point = self.spawn_point
