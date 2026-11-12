from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .gameplay import GameSystem

HIDDEN_SECONDS = 3.0
REVEAL_SECONDS = 1.0
SPAWN_SECONDS = 1.5
COUNTDOWN_SECONDS = 3.0
ACTOR_INTERVAL = 0.25
COLLECTIBLE_STEPS = 10
STORY_SPEED = 30.0
SPAWN_COLOR = (235, 235, 255)


class LevelIntro:
    def __init__(self) -> None:
        """
        Start the intro clock of a new level.
        The same clock also drives the live typing of the level story.
        made by: Mohammad Abu Aresh
        """
        self.elapsed: float = 0.0
        self.announced: int = 0

    def restart(self) -> None:
        """
        Restart the intro for a freshly loaded level.
        Clear the clock and the number of announced spawns.
        made by: Mohammad Abu Aresh
        """
        self.elapsed = 0.0
        self.announced = 0

    def update(self, delta_time: float) -> bool:
        """
        Advance the intro clock by the elapsed frame time.
        Return True while the gameplay must stay frozen.
        made by: Mohammad Abu Aresh
        """
        self.elapsed += max(delta_time, 0.0)
        return self.active

    @property
    def active(self) -> bool:
        """
        Report whether the intro is still running.
        The intro ends after the countdown has reached zero.
        made by: Mohammad Abu Aresh
        """
        return self.elapsed < self._spawn_start() + (
            SPAWN_SECONDS + COUNTDOWN_SECONDS
        )

    def maze_progress(self) -> float:
        """
        Return how much of the maze is revealed from zero to one.
        The maze stays hidden for the first seconds of the level.
        made by: Mohammad Abu Aresh
        """
        shown = (self.elapsed - HIDDEN_SECONDS) / REVEAL_SECONDS
        return min(max(shown, 0.0), 1.0)

    def visible_actor_count(self, total: int) -> int:
        """
        Return how many creatures have spawned so far.
        The player appears first and the monsters follow one by one.
        made by: Mohammad Abu Aresh
        """
        waited = self.elapsed - self._spawn_start()
        if waited < 0:
            return 0
        return min(total, 1 + int(waited / ACTOR_INTERVAL))

    def visible_collectible_count(self, total: int) -> int:
        """
        Return how many gums have spawned so far.
        Reveal them in steps so the maze fills up like a wave.
        made by: Mohammad Abu Aresh
        """
        waited = self.elapsed - self._spawn_start()
        if waited < 0:
            return 0
        done = min(waited / (SPAWN_SECONDS * 0.9), 1.0)
        return total * int(done * COLLECTIBLE_STEPS) // COLLECTIBLE_STEPS

    def countdown_number(self) -> int | None:
        """
        Return the number shown in the middle of the screen.
        Count 3, 2, 1 after everything has spawned, otherwise None.
        made by: Mohammad Abu Aresh
        """
        start = self._spawn_start() + SPAWN_SECONDS
        waited = self.elapsed - start
        if waited < 0 or waited >= COUNTDOWN_SECONDS:
            return None
        return int(COUNTDOWN_SECONDS) - int(waited)

    def countdown_fraction(self) -> float:
        """
        Return the progress of the current countdown number.
        Use it to animate the number from big to small.
        made by: Mohammad Abu Aresh
        """
        waited = self.elapsed - self._spawn_start() - SPAWN_SECONDS
        return waited - int(waited) if waited > 0 else 0.0

    def story_chars(self, total: int) -> int:
        """
        Return how many characters of the level story are typed.
        Type at a fixed speed from the start of the level.
        made by: Mohammad Abu Aresh
        """
        return min(total, int(self.elapsed * STORY_SPEED))

    def _spawn_start(self) -> float:
        """
        Return the time when the spawn phase begins.
        It comes right after the maze has been revealed.
        made by: Mohammad Abu Aresh
        """
        return HIDDEN_SECONDS + REVEAL_SECONDS


def reveal_lines(lines: list[str], chars: int) -> list[str]:
    """
    Return the part of the wrapped story that is typed so far.
    Count one extra character for the space removed by each wrap.
    made by: Mohammad Abu Aresh
    """
    shown: list[str] = []
    remaining = chars
    for line in lines:
        if remaining <= 0:
            break
        shown.append(line[:remaining])
        remaining -= len(line) + 1
    return shown


def announce_spawns(game: GameSystem, delta_time: float) -> None:
    """
    Burst particles where a creature has just spawned.
    Also keep the particles moving while the gameplay is frozen.
    made by: Mohammad Abu Aresh
    """
    intro = game.intro
    visible = intro.visible_actor_count(len(game.mobs))
    effects = game.player_creature.effects
    for actor in game.mobs[intro.announced:visible]:
        effects.burst(actor.x, actor.y, SPAWN_COLOR)
    intro.announced = visible
    effects.update(delta_time)
