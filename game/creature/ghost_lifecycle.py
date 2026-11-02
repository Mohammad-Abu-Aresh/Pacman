from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .creature import Control_creature
    from .monster import Monster


@dataclass(slots=True)
class GhostLifecycle:
    """Store per-monster Power Pellet and mode-clock state."""
    last_eaten_cycle: int = -1
    active_cycle: int = -1
    pending_cycle: int = -1
    pending_timer: float = 0.0
    mode_clock_paused: bool = False


def start_power_pellet_cycle(
    controller: Control_creature, duration: float
) -> None:
    """Start a new Power Pellet cycle for every monster.
    Activate living monsters and remember the remaining frightened time
    for monsters that are still returning to their spawn.
    made by: Mohammad Abu Aresh
    """
    controller.frightened_cycle += 1
    controller.frightened_timer = max(
        controller.frightened_timer, max(duration, 0.0)
    )
    controller.player._is_super = controller.frightened_timer > 0
    for monster in _monsters(controller):
        state = monster.lifecycle
        state.active_cycle = controller.frightened_cycle
        state.mode_clock_paused = controller.frightened_timer > 0
        if monster.live:
            state.pending_cycle = -1
            state.pending_timer = 0.0
            monster.activate_frightened(controller.frightened_timer)
        else:
            state.pending_cycle = controller.frightened_cycle
            state.pending_timer = controller.frightened_timer


def sync_returning_monsters(controller: Control_creature) -> None:
    """Synchronize returning monsters with the shared Power Pellet timer.
    Pause mode clocks for the group and expire any pending frightened
    state when the current cycle ends.
    made by: Mohammad Abu Aresh
    """
    active = controller.frightened_timer > 0
    for monster in _monsters(controller):
        state = monster.lifecycle
        state.mode_clock_paused = active
        if (
            not monster.live
            and state.pending_cycle == controller.frightened_cycle
        ):
            state.pending_timer = controller.frightened_timer
        elif not monster.live:
            state.pending_cycle = -1
            state.pending_timer = 0.0


def mark_monster_eaten(
    controller: Control_creature,
    monster: Monster,
    points_per_ghost: int,
) -> bool:
    """Eat an eligible frightened monster at most once per Power Pellet.
    Award points, record the active cycle, and begin its return to spawn.
    made by: Mohammad Abu Aresh
    """
    state = monster.lifecycle
    cycle = controller.frightened_cycle
    if not monster.frightened or state.active_cycle != cycle:
        return False
    if state.last_eaten_cycle == cycle:
        return False

    controller.player.eat(points_per_ghost)
    state.last_eaten_cycle = cycle
    state.pending_cycle = -1
    state.pending_timer = 0.0
    monster.frightened = False
    monster.frightened_timer = 0.0
    current_step = monster.next_point
    monster.die()
    monster.next_point = current_step
    set_monster_eaten_visual(monster)
    return True


def set_monster_eaten_visual(monster: Monster) -> None:
    """Render only the eyes while a monster returns to its spawn.
    Build a transparent sprite at the existing image dimensions so the
    current drawing and 2.5D layering code remains unchanged.
    made by: Mohammad Abu Aresh
    """
    import pygame

    width, height = monster.image.get_size()
    image = pygame.Surface((width, height), pygame.SRCALPHA)
    eye_width = max(4, width // 4)
    eye_height = max(5, height // 4)
    eye_y = max(1, height // 3)
    pupil_radius = max(2, min(eye_width, eye_height) // 4)
    for center_x in (width // 3, (width * 2) // 3):
        rect = pygame.Rect(
            center_x - eye_width // 2,
            eye_y,
            eye_width,
            eye_height,
        )
        pygame.draw.ellipse(image, (255, 255, 255), rect)
        pygame.draw.circle(
            image,
            (30, 60, 180),
            (center_x, eye_y + eye_height // 2),
            pupil_radius,
        )
    monster.image = image


def reactivate_eaten_monster(monster: Monster) -> bool:
    """Reactivate an eaten monster after it reaches its own spawn.
    Restore its normal sprite, then resume a newer active Power Pellet
    cycle only when its pending timer has not expired.
    made by: Mohammad Abu Aresh
    """
    if monster.live or (monster.x, monster.y) != tuple(
        float(value) for value in monster.spawn_point
    ):
        return False

    state = monster.lifecycle
    pending_cycle = state.pending_cycle
    pending_timer = state.pending_timer
    monster.live = True
    monster.is_following = True
    monster.target_point = None
    monster.next_point = None
    monster.movement_direction = (0, 0)
    monster.reverse_pending = False
    monster.frightened = False
    monster.frightened_timer = 0.0
    monster.load_size()
    state.pending_cycle = -1
    state.pending_timer = 0.0

    if pending_timer > 0 and pending_cycle != state.last_eaten_cycle:
        state.active_cycle = pending_cycle
        monster.activate_frightened(pending_timer)
    return True


def _monsters(controller: Control_creature) -> tuple[Monster, ...]:
    """Return the four monsters managed by the creature controller.
    Keep the group order consistent with the project creature registry.
    made by: Mohammad Abu Aresh
    """
    return (
        controller.BabyZombie,
        controller.Skeleton,
        controller.Enderman,
        controller.witch,
    )
