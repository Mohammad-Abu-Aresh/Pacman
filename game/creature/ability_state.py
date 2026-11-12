from __future__ import annotations
from typing import TYPE_CHECKING
from .effects import ENDER_COLOR, POTION_COLOR

if TYPE_CHECKING:
    from .creature import Control_creature


def update_group_abilities(
    controller: Control_creature, delta_time: float
) -> bool:
    """
    Advance zombie speed, slow effect, potion, teleport and arrows.
    Return True when an arrow hit the player in this update.
    made by: Mohammad Abu Aresh
    """
    player = controller.player
    controller.BabyZombie.sync_hardcore_speed()
    player.update_slow(delta_time)
    if controller.witch.update_potion(player, delta_time):
        controller.effects.burst(player.x, player.y, POTION_COLOR)
    if player.is_slowed:
        controller.effects.trail(
            player.x, player.y, POTION_COLOR, delta_time
        )
    for x, y in controller.Enderman.update_teleport(
        player, controller.maze_mape.every_cell, delta_time
    ):
        controller.effects.burst(x, y, ENDER_COLOR)
    controller.effects.update(delta_time)
    return controller.Skeleton.update_arrows(
        player, controller.maze_mape, delta_time,
        controller.frightened_timer <= 0,
    )
