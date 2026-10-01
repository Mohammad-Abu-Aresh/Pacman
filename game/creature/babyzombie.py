from .monster import Monster
from .player import Player
from ..block import Block
from photos.loderimages import Images

class BabyZombie(Monster):

    def __init__(
        self, spawn_point: tuple[int, int], is_hardcore: bool = False
    ) -> None:
        self.spawn_point = spawn_point
        self.locaion: tuple[float, float] = (
                float(self.spawn_point[0]),
                float(self.spawn_point[1]),
                )
        self.live: bool = True
        if is_hardcore and self.live:
            self.speed = 110
        self.is_hardcore: bool = is_hardcore
        self.load_size()

    # @classmethod
    def load_size(self) -> None:
        Images._update_size(
            "zombie",
            (Block.size * 0.9, Block.size * 0.5)
            )
    
    def set_hardcore_mode(self, enabled: bool) -> None:
        super().set_hardcore_mode(enabled)
        if self.live:
            self.speed = 110 if enabled else 65

    def move(self) -> None:
        pass

    def follow(self, player: Player) -> None:
        if self.live:
            self.target_point = (player.x, player.y)
        else:
            self.target_point = self.spawn_point
