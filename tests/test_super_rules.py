import os
import unittest
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from game.block import Block  # noqa: E402
from game.creature import monster as monster_module  # noqa: E402
from game.creature.babyzombie import BabyZombie  # noqa: E402
from game.creature.ghost_state import (  # noqa: E402
    check_ghost_collisions,
    reactivate_monster_at_home,
)
from game.creature.player import Player  # noqa: E402
from game.creature.skeleton import Skeleton  # noqa: E402
from game.creature.witch import Witch  # noqa: E402


def make_player(x: float, y: float) -> Player:
    player = Player.__new__(Player)
    player.x = x
    player.y = y
    player.speed = 0.1
    player._normal_speed = 0.1
    player._slow_left = 0.0
    return player


def open_lane() -> Any:
    width = 42
    rows = ["#" * width, "#" + "." * (width - 2) + "#", "#" * width]
    return SimpleNamespace(
        every_cell=[[char == "#" for char in row] for row in rows]
    )


class MonsterAbilityStateTests(unittest.TestCase):
    def setUp(self) -> None:
        Block.size = 40

    def test_zombie_is_fast_only_while_red_in_hardcore(self) -> None:
        zombie = BabyZombie((1, 1), True)
        zombie.sync_hardcore_speed()
        self.assertEqual(zombie.speed, 110)
        zombie.frightened = True
        zombie.sync_hardcore_speed()
        self.assertEqual(zombie.speed, 65)
        zombie.frightened = False
        zombie.sync_hardcore_speed()
        self.assertEqual(zombie.speed, 110)

    def test_zombie_stays_normal_without_hardcore(self) -> None:
        zombie = BabyZombie((1, 1), False)
        zombie.sync_hardcore_speed()
        self.assertEqual(zombie.speed, 65)

    def test_frightened_skeleton_does_not_shoot(self) -> None:
        skeleton = Skeleton((1, 1), True)
        skeleton.frightened = True
        skeleton.update_arrows(SimpleNamespace(x=10, y=1), open_lane(), 0.1)
        self.assertEqual(skeleton.active_arrows, [])

    def test_red_skeleton_shoots_even_while_super_is_running(self) -> None:
        skeleton = Skeleton((1, 1), True)
        skeleton.frightened = False
        player: Any = SimpleNamespace(x=10, y=1)
        skeleton.update_arrows(player, open_lane(), 0.1, False)
        self.assertEqual(len(skeleton.active_arrows), 1)

    def test_respawned_skeleton_turns_red_and_shoots_again(self) -> None:
        skeleton = Skeleton((1, 1), True)
        skeleton.frightened = True
        skeleton.die()
        self.assertTrue(reactivate_monster_at_home(skeleton))
        self.assertFalse(skeleton.frightened)
        player: Any = SimpleNamespace(x=10, y=1)
        skeleton.update_arrows(player, open_lane(), 0.1, False)
        self.assertEqual(len(skeleton.active_arrows), 1)

    def test_arrows_cannot_hurt_while_super_is_running(self) -> None:
        skeleton = Skeleton((1, 1), True)
        mape = open_lane()
        player: Any = SimpleNamespace(x=10, y=1)
        skeleton.update_arrows(player, mape, 1 / 60, False)
        hits = [
            skeleton.update_arrows(player, mape, 1 / 60, False)
            for _ in range(60)
        ]
        self.assertNotIn(True, hits)
        self.assertFalse(skeleton.active_arrows[0].hit_player)

    def test_frightened_witch_does_not_throw_but_red_one_does(self) -> None:
        witch = Witch((5, 5), True)
        player = make_player(6, 5)
        witch.frightened = True
        witch.update_potion(player, 1 / 60)
        self.assertEqual(player.speed, 0.1)
        witch.frightened = False
        witch.update_potion(player, 1 / 60)
        self.assertAlmostEqual(player.speed, 0.035)


class SuperSafetyTests(unittest.TestCase):
    def setUp(self) -> None:
        Block.size = 40

    def controller(self, timer: float) -> Any:
        monsters = [
            Skeleton((1, 1), True),
            BabyZombie((30, 1), True),
            Skeleton((31, 1), True),
            Skeleton((32, 1), True),
        ]
        return SimpleNamespace(
            player=SimpleNamespace(x=1.0, y=1.0, eat=lambda points: points),
            Skeleton=monsters[0],
            BabyZombie=monsters[1],
            Enderman=monsters[2],
            witch=monsters[3],
            frightened_cycle=1,
            frightened_timer=timer,
        )

    def test_monster_contact_is_safe_during_super(self) -> None:
        controller = self.controller(5.0)
        self.assertFalse(check_ghost_collisions(controller, 200))

    def test_monster_contact_is_deadly_outside_super(self) -> None:
        controller = self.controller(0.0)
        self.assertTrue(check_ghost_collisions(controller, 200))

    def test_monsters_flee_instead_of_chasing_during_super(self) -> None:
        skeleton = Skeleton((1, 1), True)
        skeleton.target_point = (5, 5)
        grid = [[False] * 8 for _ in range(8)]
        skeleton.lifecycle.mode_clock_paused = True
        with patch.object(
            monster_module.PathFinder, "next_step_frightened",
            return_value=(2, 1),
        ) as flee, patch.object(
            monster_module.PathFinder, "next_step_towards",
            return_value=(1, 2),
        ) as chase:
            step = skeleton._choose_next_point(grid, (1, 1))
        self.assertEqual(step, (2, 1))
        flee.assert_called_once()
        chase.assert_not_called()

    def test_monsters_chase_again_after_super(self) -> None:
        skeleton = Skeleton((1, 1), True)
        skeleton.target_point = (5, 5)
        grid = [[False] * 8 for _ in range(8)]
        with patch.object(
            monster_module.PathFinder, "next_step_towards",
            return_value=(1, 2),
        ) as chase:
            step = skeleton._choose_next_point(grid, (1, 1))
        self.assertEqual(step, (1, 2))
        chase.assert_called_once()


if __name__ == "__main__":
    unittest.main()
