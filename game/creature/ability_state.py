from __future__ import annotations
from typing import TYPE_CHECKING
from .effects import POTION_COLOR

if TYPE_CHECKING:
    from .creature import Control_creature


def update_group_abilities(
    controller: Control_creature, delta_time: float
) -> bool:
    player = controller.player
    controller.BabyZombie.sync_hardcore_speed()
    player.update_slow(delta_time)
    if controller.witch.update_potion(player, delta_time):
        controller.effects.burst(player.x, player.y, POTION_COLOR)
    if player.is_slowed:
        controller.effects.trail(
            player.x, player.y, POTION_COLOR, delta_time
        )
    controller.effects.update(delta_time)
    return controller.Skeleton.update_arrows(
        player, controller.maze_mape, delta_time,
        controller.frightened_timer <= 0,
    )
