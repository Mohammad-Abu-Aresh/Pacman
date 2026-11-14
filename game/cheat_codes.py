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


def apply_next_level_cheat(game: GameSystem, pressed: bool) -> bool:
    """
    Jump to the next level when the level cheat key is newly pressed.
    Work during the intro, the countdown and the gameplay alike.
    made by: Mohammad Abu Aresh
    """
    jumped = pressed and not game.next_key_down
    game.next_key_down = pressed
    if jumped:
        game.next_level()
    return jumped
