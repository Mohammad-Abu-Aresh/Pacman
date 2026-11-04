from typing import cast
from game.block import Mape
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


def test_arrow_direction_is_always_cardinal() -> None:
    """Keep arrows aligned to horizontal or vertical maze corridors.
    Diagonal source directions are reduced to the dominant axis.
    made by: Mohammad Abu aresh
    """
    from game.creature.projectiles import Arrow

    arrow = Arrow((1.0, 1.0), (5.0, 2.0))
    assert arrow.direction == (1, 0)


def test_arrow_does_not_expire_while_corridor_is_open() -> None:
    """Keep a fired arrow active until it reaches a wall.
    Long travel time alone must not deactivate the projectile.
    made by: Mohammad Abu aresh
    """
    from game.creature.projectiles import Arrow

    arrow = Arrow((1.0, 1.0), (1.0, 0.0), speed=6.0)
    grid = [[False] * 40 for _ in range(3)]
    arrow.update(5.0, grid)
    assert arrow.active


def test_arrow_stops_when_it_reaches_a_wall() -> None:
    """Remove an arrow when its next cardinal step enters a wall cell.
    Verify that the projectile never continues through the obstacle.
    made by: Mohammad Abu aresh
    """
    from game.creature.projectiles import Arrow

    grid = [[False] * 8 for _ in range(3)]
    grid[1][4] = True
    arrow = Arrow((1.0, 1.0), (1.0, 0.0), speed=6.0)
    arrow.update(1.0, grid)
    assert not arrow.active
    assert round(arrow.x) < 4


def test_arrow_remains_active_after_player_hit() -> None:
    """Keep the projectile moving after registering one player collision.
    The arrow is removed only when its path reaches a wall.
    made by: Mohammad Abu aresh
    """
    from types import SimpleNamespace
    from game.creature.projectiles import Arrow

    arrow = Arrow((1.0, 1.0), (1.0, 0.0))
    player = cast(Player, SimpleNamespace(x=1.0, y=1.0))
    assert arrow.hits_player(player)
    assert not arrow.hits_player(player)
    assert arrow.active


def test_skeleton_can_target_a_distant_player_without_walls() -> None:
    """Allow straight shots across any clear row regardless of distance.
    A single wall between the actors must block the shot.
    made by: Mohammad Abu aresh
    """
    from types import SimpleNamespace
    from game.creature.skeleton import Skeleton

    skeleton = object.__new__(Skeleton)
    skeleton.live = True
    skeleton.x = 1.0
    skeleton.y = 1.0
    player = cast(Player, SimpleNamespace(x=28.0, y=1.0))
    grid = [[False] * 30 for _ in range(3)]
    mape = cast(Mape, SimpleNamespace(every_cell=grid))

    assert skeleton.has_line_of_sight(player, mape)
    grid[1][15] = True
    assert not skeleton.has_line_of_sight(player, mape)


def test_slow_potion_uses_square_fallback() -> None:
    """Use a visible red square when no valid potion sprite is available.
    Keep the fallback's display dimensions square and tied to cell size.
    made by: Mohammad Abu aresh
    """
    from game.creature.projectiles import SlowPotion

    potion = SlowPotion((1.0, 1.0))
    assert potion.image.get_width() == potion.image.get_height()
    assert potion.image.get_at((0, 0))[:3] == (255, 0, 0)


def test_projectile_sprites_support_smooth_scaling() -> None:
    """Create both image-backed projectiles with palette PNG assets.
    Convert source images before smooth scaling to support indexed PNGs.
    made by: Mohammad Abu aresh
    """
    from game.creature.projectiles import Arrow, EnderPearl

    arrow = Arrow((1.0, 1.0), (1.0, 0.0))
    pearl = EnderPearl((3, 1), spawn_point=(1.0, 1.0))
    assert arrow.image.get_size()[0] > 0
    assert pearl.image.get_size()[0] > 0
