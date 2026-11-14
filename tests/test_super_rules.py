import os
import unittest
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from game.block import Block  # noqa: E402
from game.creature import ghost_lifecycle as lifecycle_module  # noqa: E402
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
    """Create a player object without running its constructor.
    Set only the fields used by the slow potion logic.
    made by: Mohammad Abu Aresh
    """
    player = Player.__new__(Player)
    player.x = x
    player.y = y
    player.speed = 0.1
    player._normal_speed = 0.1
    player._slow_left = 0.0
    return player


def open_lane() -> Any:
    """Build a long open lane as a light map object.
    Only the every_cell grid is provided.
    made by: Mohammad Abu Aresh
    """
    width = 42
    rows = ["#" * width, "#" + "." * (width - 2) + "#", "#" * width]
    return SimpleNamespace(
        every_cell=[[char == "#" for char in row] for row in rows]
    )


class MonsterAbilityStateTests(unittest.TestCase):
    def setUp(self) -> None:
        """Set the block size used by the monster constructors.
        Run it before every ability state test.
        made by: Mohammad Abu Aresh
        """
        Block.size = 40

    def test_zombie_is_fast_only_while_red_in_hardcore(self) -> None:
        """Verify the zombie is fast only while red in hardcore.
        Check it slows down while frightened and speeds up after.
        made by: Mohammad Abu Aresh
        """
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
        """Verify the speed boost never applies outside hardcore.
        The zombie must keep the normal speed.
        made by: Mohammad Abu Aresh
        """
        zombie = BabyZombie((1, 1), False)
        zombie.sync_hardcore_speed()
        self.assertEqual(zombie.speed, 65)

    def test_frightened_skeleton_does_not_shoot(self) -> None:
        """Verify a frightened skeleton creates no arrow.
        Check it with the regular arrow update.
        made by: Mohammad Abu Aresh
        """
        skeleton = Skeleton((1, 1), True)
        skeleton.frightened = True
        player: Any = SimpleNamespace(x=10, y=1)
        skeleton.update_arrows(player, open_lane(), 0.1)
        self.assertEqual(skeleton.active_arrows, [])

    def test_red_skeleton_shoots_even_while_super_is_running(self) -> None:
        """Verify a red skeleton shoots while the super is still active.
        The ability depends on its own color.
        made by: Mohammad Abu Aresh
        """
        skeleton = Skeleton((1, 1), True)
        skeleton.frightened = False
        player: Any = SimpleNamespace(x=10, y=1)
        skeleton.update_arrows(player, open_lane(), 0.1)
        self.assertEqual(len(skeleton.active_arrows), 1)

    def test_respawned_skeleton_turns_red_and_shoots_again(self) -> None:
        """Verify an eaten skeleton turns red when it respawns.
        Check that it shoots again with the super still running.
        made by: Mohammad Abu Aresh
        """
        skeleton = Skeleton((1, 1), True)
        skeleton.frightened = True
        skeleton.die()
        self.assertTrue(reactivate_monster_at_home(skeleton))
        self.assertFalse(skeleton.frightened)
        player: Any = SimpleNamespace(x=10, y=1)
        skeleton.update_arrows(player, open_lane(), 0.1)
        self.assertEqual(len(skeleton.active_arrows), 1)

    def test_red_skeleton_arrows_hurt_while_super_is_running(self) -> None:
        """Verify an arrow of a red skeleton still hurts during the super.
        Only the color of the skeleton decides, not the super timer.
        made by: Mohammad Abu Aresh
        """
        skeleton = Skeleton((1, 1), True)
        mape = open_lane()
        player: Any = SimpleNamespace(x=10, y=1)
        skeleton.update_arrows(player, mape, 1 / 60)
        hits = [
            skeleton.update_arrows(player, mape, 1 / 60) for _ in range(60)
        ]
        self.assertEqual(hits.count(True), 1)

    def test_frightened_witch_does_not_throw_but_red_one_does(self) -> None:
        """Verify a frightened witch throws no potion.
        Check a red witch throws one and the potion slows the player.
        made by: Mohammad Abu Aresh
        """
        witch = Witch((5, 5), True)
        player = make_player(6, 5)
        witch.frightened = True
        witch.update_potion(player, 1 / 60)
        self.assertEqual(player.speed, 0.1)
        self.assertEqual(witch.potions, [])
        witch.frightened = False
        for _ in range(60):
            witch.update_potion(player, 1 / 60)
        self.assertAlmostEqual(player.speed, 0.035)


class CollisionRuleTests(unittest.TestCase):
    def setUp(self) -> None:
        """Set the block size and silence the eaten sprite drawing.
        Run it before every collision test.
        made by: Mohammad Abu Aresh
        """
        Block.size = 40
        patcher = patch.object(
            lifecycle_module, "set_monster_eaten_visual"
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def controller(self, timer: float) -> Any:
        """Build a light controller with the player on a skeleton.
        The other monsters stay far away and the player records points.
        made by: Mohammad Abu Aresh
        """
        monsters = [
            Skeleton((1, 1), True),
            BabyZombie((30, 1), True),
            Skeleton((31, 1), True),
            Skeleton((32, 1), True),
        ]
        player = SimpleNamespace(x=1.0, y=1.0, points=0)
        player.eat = lambda points: setattr(
            player, "points", player.points + points
        )
        return SimpleNamespace(
            player=player,
            Skeleton=monsters[0],
            BabyZombie=monsters[1],
            Enderman=monsters[2],
            witch=monsters[3],
            frightened_cycle=1,
            frightened_timer=timer,
        )

    def test_red_monster_kills_while_super_is_running(self) -> None:
        """Verify touching a red monster hurts even during the super.
        The monster stays alive because it is not frightened.
        made by: Mohammad Abu Aresh
        """
        controller = self.controller(5.0)
        self.assertTrue(check_ghost_collisions(controller, 200))
        self.assertTrue(controller.Skeleton.live)

    def test_red_monster_kills_outside_super(self) -> None:
        """Verify touching a red monster hurts without any super.
        The collision must be reported with a stopped timer.
        made by: Mohammad Abu Aresh
        """
        controller = self.controller(0.0)
        self.assertTrue(check_ghost_collisions(controller, 200))

    def test_blue_monster_dies_and_the_player_survives(self) -> None:
        """Verify touching a frightened monster eats it.
        The player gets the points and is not hit.
        made by: Mohammad Abu Aresh
        """
        controller = self.controller(5.0)
        controller.Skeleton.frightened = True
        controller.Skeleton.lifecycle.active_cycle = 1
        self.assertFalse(check_ghost_collisions(controller, 200))
        self.assertFalse(controller.Skeleton.live)
        self.assertEqual(controller.player.points, 200)

    def test_blue_monster_never_kills_the_player(self) -> None:
        """Verify a frightened monster is harmless even if not edible.
        Use a monster that belongs to an older power pellet cycle.
        made by: Mohammad Abu Aresh
        """
        controller = self.controller(5.0)
        controller.Skeleton.frightened = True
        controller.Skeleton.lifecycle.active_cycle = 0
        self.assertFalse(check_ghost_collisions(controller, 200))
        self.assertTrue(controller.Skeleton.live)

    def test_exactly_one_of_them_dies_on_contact(self) -> None:
        """Verify a contact kills either the player or the monster.
        Check both a red and a frightened monster.
        made by: Mohammad Abu Aresh
        """
        for frightened in (False, True):
            controller = self.controller(5.0)
            controller.Skeleton.frightened = frightened
            controller.Skeleton.lifecycle.active_cycle = 1
            hit = check_ghost_collisions(controller, 200)
            self.assertNotEqual(hit, not controller.Skeleton.live)

    def test_eaten_monster_respawns_red_and_kills_during_super(self) -> None:
        """Verify an eaten monster is dangerous again when it respawns.
        The super timer is still running when it touches the player.
        made by: Mohammad Abu Aresh
        """
        controller = self.controller(5.0)
        skeleton = controller.Skeleton
        skeleton.frightened = True
        skeleton.lifecycle.active_cycle = 1
        check_ghost_collisions(controller, 200)
        self.assertFalse(skeleton.live)
        skeleton.x, skeleton.y = 1.0, 1.0
        self.assertTrue(reactivate_monster_at_home(skeleton))
        self.assertFalse(skeleton.frightened)
        self.assertTrue(check_ghost_collisions(controller, 200))


class ChaseRuleTests(unittest.TestCase):
    def setUp(self) -> None:
        """Set the block size and prepare a skeleton with a target.
        Patch both path routines to return different steps.
        made by: Mohammad Abu Aresh
        """
        Block.size = 40
        self.skeleton = Skeleton((1, 1), True)
        self.skeleton.target_point = (5, 5)
        self.grid = [[False] * 8 for _ in range(8)]

    def routes(self) -> tuple[Any, Any, Any]:
        """Run one route choice with both path routines replaced.
        Return the chosen step and the two replaced routines.
        made by: Mohammad Abu Aresh
        """
        with patch.object(
            monster_module.PathFinder, "next_step_frightened",
            return_value=(2, 1),
        ) as flee, patch.object(
            monster_module.PathFinder, "next_step_towards",
            return_value=(1, 2),
        ) as chase:
            step = self.skeleton._choose_next_point(self.grid, (1, 1))
        return step, flee, chase

    def test_blue_monsters_flee(self) -> None:
        """Verify a frightened monster uses the frightened route.
        The chase route must not be used.
        made by: Mohammad Abu Aresh
        """
        self.skeleton.frightened = True
        step, flee, chase = self.routes()
        self.assertEqual(step, (2, 1))
        chase.assert_not_called()

    def test_red_monsters_keep_chasing_while_super_is_running(self) -> None:
        """Verify a red monster chases while the super timer runs.
        Only the monster color decides the route.
        made by: Mohammad Abu Aresh
        """
        self.skeleton.lifecycle.mode_clock_paused = True
        step, flee, chase = self.routes()
        self.assertEqual(step, (1, 2))
        flee.assert_not_called()

    def test_monsters_chase_after_super(self) -> None:
        """Verify monsters use the chase route without any super.
        The frightened route must not be used.
        made by: Mohammad Abu Aresh
        """
        step, flee, chase = self.routes()
        self.assertEqual(step, (1, 2))
        chase.assert_called_once()


if __name__ == "__main__":
    unittest.main()
