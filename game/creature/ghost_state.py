from __future__ import annotations
from typing import TYPE_CHECKING
import pygame
from photos.loderimages import Images

if TYPE_CHECKING:
    from .creature import Control_creature
    from .monster import Monster

def set_monster_frightened_visual(
    monster: Monster, enabled: bool
) -> None:
    """
    Switch a monster to the blue frightened image or restore its
    normal image.
    Scale the blue image to the monster current sprite
    dimensions.
    made by: Mohammad Abu Aresh
    """
    if enabled:
        monster.image = pygame.transform.scale(
            Images.blue_ghost, monster.image.get_size()
        )
    else:
        monster.load_size()


def step_towards(current: float, target: float, distance: float) -> float:
    """
    Move a scalar value toward its target without passing the
    target.
    Return the target directly when the remaining distance is
    small enough.
    made by: Mohammad Abu Aresh
    """
    remaining = target - current
    if abs(remaining) <= distance:
        return target
    return current + (distance if remaining > 0 else -distance)


def reset_monster_ai(monster: Monster) -> None:
    """
    Restore a monster to its initial active AI and visual state.
    Reset targets, movement, mode timing, reversal, and
    frightened fields.
    made by: Mohammad Abu Aresh
    """
    set_monster_frightened_visual(monster, False)
    monster.target_point = None
    monster.next_point = None
    monster.live = True
    monster.is_following = True
    monster.movement_direction = (0, 0)
    monster.mode_index = 0
    monster.mode, monster.mode_timer = monster.MODE_SCHEDULE[0]
    monster.reverse_pending = False
    monster.frightened = False
    monster.frightened_timer = 0.0


def activate_monster_frightened(monster: Monster, duration: float) -> None:
    """
    Activate frightened mode for a living monster.
    Update its visual, extend its timer, request reversal, and
    clear its target.
    made by: Mohammad Abu Aresh
    """
    if not monster.live:
        return
    if not monster.frightened:
        set_monster_frightened_visual(monster, True)
    monster.frightened = True
    monster.frightened_timer = max(
        monster.frightened_timer, max(duration, 0.0)
    )
    monster.reverse_pending = True
    monster.target_point = None


def update_monster_mode(monster: Monster, delta_time: float) -> None:
    """
    Advance a monster through the configured Scatter and Chase
    schedule.
    Request a direction reversal and clear the target when a
    mode changes.
    made by: Mohammad Abu Aresh
    """
    monster.mode_timer -= delta_time
    while (
        monster.mode_timer <= 0
        and monster.mode_index < len(monster.MODE_SCHEDULE) - 1
    ):
        previous_timer = monster.mode_timer
        monster.mode_index += 1
        monster.mode, duration = monster.MODE_SCHEDULE[monster.mode_index]
        monster.mode_timer = duration + previous_timer
        monster.reverse_pending = True
        monster.target_point = None


def activate_group_frightened(
    controller: Control_creature, duration: float
) -> None:
    """
    Activate frightened mode for every monster in the creature
    controller.
    Extend the group timer and enable the player super-state
    indicator.
    made by: Mohammad Abu Aresh
    """
    controller.frightened_timer = max(
        controller.frightened_timer, max(duration, 0.0)
    )
    controller.player._is_super = controller.frightened_timer > 0
    for monster in (
        controller.BabyZombie, controller.Skeleton,
        controller.Enderman, controller.witch
    ):
        monster.activate_frightened(duration)


def update_group_frightened(
    controller: Control_creature, delta_time: float
) -> None:
    """
    Decrease the shared frightened timer without allowing it
    below zero.
    Keep the player super-state indicator synchronized with the
    timer.
    made by: Mohammad Abu Aresh
    """
    if controller.frightened_timer <= 0:
        return
    controller.frightened_timer = max(
        0.0, controller.frightened_timer - max(delta_time, 0.0)
    )
    controller.player._is_super = controller.frightened_timer > 0


def reset_group_frightened(controller: Control_creature) -> None:
    """
    Clear the shared frightened timer and the player super-state
    indicator.
    Use this when the creature group returns to its normal
    state.
    made by: Mohammad Abu Aresh
    """
    controller.frightened_timer = 0.0
    controller.player._is_super = False


def reactivate_monster_at_home(monster: Monster) -> bool:
    """
    Reactivate a dead monster after it reaches its spawn
    coordinates.
    Reset its movement state and return whether reactivation
    occurred.
    made by: Mohammad Abu Aresh
    """
    if monster.live or (monster.x, monster.y) != tuple(
        float(value) for value in monster.spawn_point
    ):
        return False
    monster.live = True
    monster.is_following = True
    monster.target_point = None
    monster.next_point = None
    monster.movement_direction = (0, 0)
    monster.reverse_pending = False
    return True


def check_ghost_collisions(
    controller: Control_creature, points_per_ghost: int
) -> bool:
    """
    Check player overlap against every living monster.
    Eat frightened monsters for points and report contact with a
    dangerous one.
    made by: Mohammad Abu Aresh
    """
    player_hit = False
    for monster in (
        controller.BabyZombie, controller.Skeleton,
        controller.Enderman, controller.witch
    ):
        if not monster.live:
            continue
        dx = controller.player.x - monster.x
        dy = controller.player.y - monster.y
        if dx * dx + dy * dy > 0.4:
            continue
        if monster.frightened:
            controller.player.eat(points_per_ghost)
            monster.die()
        else:
            player_hit = True
    return player_hit
