from game.creature.monster import Monster
from game.creature.player import Player


class MonsterSpeedProbe(Monster):
    def follow(self, player: Player) -> None:
        pass

    def load_size(self) -> None:
        pass


def test_hardcore_monster_loses_abilities_when_frightened() -> None:
    """Disable Hardcore powers while a monster is frightened.
    Re-enable the ability gate after the frightened state ends.
    made by: Mohammad Abu aresh
    """
    monster = MonsterSpeedProbe((1, 1), is_hardcore=True)
    assert monster.hardcore_active
    monster.frightened = True
    assert not monster.hardcore_active


def test_hardcore_baby_zombie_uses_normal_speed_when_frightened() -> None:
    """Use the standard mob speed while a Hardcore BabyZombie is scared.
    Keep its frightened movement multiplier shared with other monsters.
    made by: Mohammad Abu aresh
    """
    monster = MonsterSpeedProbe((1, 1), is_hardcore=True)
    monster.speed = 110
    monster.frightened = True
    assert monster.movement_speed == 65
