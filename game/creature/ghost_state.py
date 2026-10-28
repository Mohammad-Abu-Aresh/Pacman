from __future__ import annotations
from typing import TYPE_CHECKING
import pygame
from photos.loderimages import Images

if TYPE_CHECKING:
    from .creature import Control_creature
    from .monster import Monster

MODE_SCHEDULE: tuple[tuple[str, float], ...] = (
    ("scatter", 7.0),
    ("chase", 20.0),
    ("scatter", 7.0),
    ("chase", 20.0),
    ("scatter", 5.0),
    ("chase", 20.0),
    ("scatter", 5.0),
    ("chase", float("inf")),
)


def set_monster_frightened_visual(
    monster: Monster, enabled: bool
) -> None:
    if enabled:
        monster.image = pygame.transform.scale(
            Images.blue_ghost, monster.image.get_size()
        )
    else:
        monster.load_size()


def step_towards(current: float, target: float, distance: float) -> float:
    remaining = target - current
    if abs(remaining) <= distance:
        return target
    return current + (distance if remaining > 0 else -distance)


def reset_monster_ai(monster: Monster) -> None:
    set_monster_frightened_visual(monster, False)
    monster.target_point = None
    monster.next_point = None
    monster.live = True
    monster.is_following = True
    monster.movement_direction = (0, 0)
    monster.mode_index = 0
    monster.mode, monster.mode_timer = MODE_SCHEDULE[0]
    monster.reverse_pending = False
    monster.frightened = False
    monster.frightened_timer = 0.0


def activate_monster_frightened(monster: Monster, duration: float) -> None:
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
    monster.mode_timer -= delta_time
    while (
        monster.mode_timer <= 0
        and monster.mode_index < len(MODE_SCHEDULE) - 1
    ):
        previous_timer = monster.mode_timer
        monster.mode_index += 1
        monster.mode, duration = MODE_SCHEDULE[monster.mode_index]
        monster.mode_timer = duration + previous_timer
        monster.reverse_pending = True
        monster.target_point = None


def activate_group_frightened(
    controller: Control_creature, duration: float
) -> None:
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
    if controller.frightened_timer <= 0:
        return
    controller.frightened_timer = max(
        0.0, controller.frightened_timer - max(delta_time, 0.0)
    )
    controller.player._is_super = controller.frightened_timer > 0


def reset_group_frightened(controller: Control_creature) -> None:
    controller.frightened_timer = 0.0
    controller.player._is_super = False


def reactivate_monster_at_home(monster: Monster) -> bool:
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
