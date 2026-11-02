from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .creature import Control_creature

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

LEVEL_TWO_TO_FOUR: tuple[tuple[str, float], ...] = (
    ("scatter", 7.0),
    ("chase", 20.0),
    ("scatter", 7.0),
    ("chase", 20.0),
    ("scatter", 5.0),
    ("chase", 1033.0),
    ("scatter", 1 / 60),
    ("chase", float("inf")),
)

LEVEL_FIVE_PLUS: tuple[tuple[str, float], ...] = (
    ("scatter", 5.0),
    ("chase", 20.0),
    ("scatter", 5.0),
    ("chase", 20.0),
    ("scatter", 5.0),
    ("chase", 1037.0),
    ("scatter", 1 / 60),
    ("chase", float("inf")),
)


def mode_schedule_for_level(level: int) -> tuple[tuple[str, float], ...]:
    """Return the original arcade Scatter and Chase schedule for a level.
    Use the level-one schedule for level one and the correct later-level
    timing bands for levels two through four and levels five onward.
    made by: Mohammad Abu Aresh
    """
    if level >= 5:
        return LEVEL_FIVE_PLUS
    if level >= 2:
        return LEVEL_TWO_TO_FOUR
    return MODE_SCHEDULE


def set_group_level(controller: Control_creature, level: int) -> None:
    """Apply a level-specific mode schedule to every monster.
    Reset each monster to the first Scatter phase for the new level.
    made by: Mohammad Abu Aresh
    """
    schedule = mode_schedule_for_level(level)
    for monster in (
        controller.BabyZombie, controller.Skeleton,
        controller.Enderman, controller.witch,
    ):
        monster.MODE_SCHEDULE = schedule
        monster.reset_ai()
