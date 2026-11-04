from types import SimpleNamespace
from typing import Any, cast

import pygame
import pytest

from game import game_renderer
from game.block import Block, Mape
from game.creature.skeleton import Skeleton


def test_arrows_are_drawn_before_world_sprites(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []
    screen = SimpleNamespace(
        blit=lambda *_args: calls.append("background")
    )
    world = SimpleNamespace(
        draw=lambda *_args: calls.append("world")
    )
    game = SimpleNamespace(
        background=object(),
        world_renderer=world,
        maze_map=object(),
        mobs=(),
        collectibles=(),
    )

    monkeypatch.setattr(game_renderer.Images, "screen", screen)
    monkeypatch.setattr(
        game_renderer,
        "draw_arrow_projectiles",
        lambda _game: calls.append("arrows"),
    )
    monkeypatch.setattr(
        game_renderer,
        "draw_hardcore_abilities",
        lambda _game: calls.append("other_abilities"),
    )
    monkeypatch.setattr(
        game_renderer,
        "draw_hud",
        lambda _game: calls.append("hud"),
    )

    game_renderer.draw_game(cast(Any, game))

    assert calls == [
        "background",
        "arrows",
        "world",
        "other_abilities",
        "hud",
    ]


def test_wider_skeleton_keeps_its_visual_center(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(Block, "size", 100)
    skeleton = object.__new__(Skeleton)
    skeleton.image = pygame.Surface((120, 180))
    skeleton.x = 2.0
    skeleton.y = 3.0
    mape = cast(
        Mape,
        SimpleNamespace(origin_x=10, origin_y=20),
    )

    rect = skeleton.get_render_rect(mape)

    assert rect.size == (120, 180)
    assert rect.center == (325, 360)


def test_arrow_direction_stays_on_cardinal_axes() -> None:
    from game.creature.projectiles import Arrow

    directions = [
        Arrow((1.0, 1.0), (1.0, 0.0)).direction,
        Arrow((1.0, 1.0), (-1.0, 0.0)).direction,
        Arrow((1.0, 1.0), (0.0, -1.0)).direction,
        Arrow((1.0, 1.0), (0.0, 1.0)).direction,
    ]

    assert directions == [
        (1, 0),
        (-1, 0),
        (0, -1),
        (0, 1),
    ]
