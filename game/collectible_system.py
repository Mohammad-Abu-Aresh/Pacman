from typing import TYPE_CHECKING
from .creature.spawn_point import Netherite

if TYPE_CHECKING:
    from .gameplay import GameSystem


def eat_pacgums(game: GameSystem) -> bool:
    """Process collectible overlap and apply its score or power effect.
    Advance the level after every collectible on the current maze is eaten.
    made by: Mohammad Abu Aresh
    """
    player = game.player_creature.player
    player_x = int(player.x + 0.5)
    player_y = int(player.y + 0.5)
    for item in game.collectibles:
        if item.is_eaten or (item.x, item.y) != (player_x, player_y):
            continue
        item.eaten()
        player.eat(item.points)
        if isinstance(item, Netherite):
            game.player_creature.activate_frightened(
                max(float(player._super_timer), 1.0)
            )
    if game.collectibles and all(item.is_eaten for item in game.collectibles):
        game.next_level()
        return True
    return False
