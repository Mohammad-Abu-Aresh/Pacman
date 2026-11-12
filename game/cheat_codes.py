from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .gameplay import GameSystem


def apply_heart_cheat(game: GameSystem, pressed: bool) -> bool:
    """
    Add one heart when the heart cheat key is newly pressed.
    Holding the key adds a single heart until it is released.
    made by: Mohammad Abu Aresh
    """
    gained = pressed and not game.heart_key_down
    game.heart_key_down = pressed
    if gained:
        game.player_creature.player.add_life()
        game.lives = game.player_creature.player._lives
    return gained
