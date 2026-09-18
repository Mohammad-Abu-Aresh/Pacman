import math
import random
from abc import ABC, abstractmethod
from .creature import Creature, Player
from ..block import Mape


class Monster(Creature, ABC):

    def __init__(
        self, spawn_point: tuple[int, int], is_hardcore: bool = False
    ) -> None:
        super().__init__(spawn_point)
        self.spawn_point: tuple[int, int] = spawn_point
        self.target_point: tuple[int, int] = spawn_point
        self.live: bool = True
        self.speed: int = 65  # 65% of player speed
        self.is_following: bool = True
        self.is_hardcore: bool = is_hardcore

    @abstractmethod
    def follow(self, player: Player) -> None:
        pass

    def set_hardcore_mode(self, enabled: bool) -> None:
        self.is_hardcore = enabled

    def die(self) -> None:
        """
        sets the monster to dead state and
        resets its target to spawn point
        """
        self.live = False
        self.is_following = False
        self.target_point = self.spawn_point


# ===============================================
# hardcore objects (only used in hardcore mode)
# ===============================================

class Arrow:

    def __init__(
        self, spawn_point: tuple[int, int],
        direction: int, speed: int = 300
    ) -> None:
        self.x: int = spawn_point[0]
        self.y: int = spawn_point[1]
        self.direction: int = direction
        self.speed: int = speed  # 300% of player speed

    def move(self) -> None:
        pass

    def draw(self) -> None:
        pass


class EnderPearl:

    def __init__(self, target_point: tuple[int, int]) -> None:
        self.target_x: int = target_point[0]
        self.target_y: int = target_point[1]

    def draw(self) -> None:
        pass


class SlowPotion:

    def __init__(self, position: tuple[int, int], duration: int = 5) -> None:
        self.x: int = position[0]
        self.y: int = position[1]
        self.duration: int = duration  # slowdown duration in seconds

    def apply_effect(self, player: Player) -> None:
        player.update_speed(35, self.duration)  # slow down the player

    def draw(self) -> None:
        pass


# ========================
# Monster Classes
# ========================

class BabyZombie(Monster):

    def __init__(
        self, spawn_point: tuple[int, int], is_hardcore: bool = False
    ) -> None:
        super().__init__(spawn_point, is_hardcore)
        if self.is_hardcore and self.live:
            self.speed = 110

    def set_hardcore_mode(self, enabled: bool) -> None:
        super().set_hardcore_mode(enabled)
        if self.live:
            self.speed = 110 if enabled else 65

    def move(self) -> None:
        pass

    def draw(self) -> None:
        pass

    def follow(self, player: Player) -> None:
        if self.live:
            self.target_point = (player.x, player.y)
        else:
            self.target_point = self.spawn_point


class Skeleton(Monster):

    def __init__(
        self, spawn_point: tuple[int, int], is_hardcore: bool = False
    ) -> None:
        super().__init__(spawn_point, is_hardcore)
        self.shoot_cooldown: float = 3.0  # cooldown between shots in seconds
        self.active_arrows: list[Arrow] = []  # if len(arr) > 0 dont shot again
        self.direction: int = 0
        # tempr = 0 becose ge is not folowing a target yet

    def has_line_of_sight(
        self, player: Player, mape: Mape
    ) -> bool:
        """
        Checks if the skeleton and Player are in the same row or column
        with no wall collisions between them
        """
        if not self.live:
            return False

        grid = mape.every_cell

        # Same column check
        if self.x == player.x:
            min_y, max_y = min(self.y, player.y), max(self.y, player.y)
            for y in range(min_y + 1, max_y):
                if grid[y][self.x]:  # true if there is a wall
                    return False
            return True

        # Same row check
        if self.y == player.y:
            min_x, max_x = min(self.x, player.x), max(self.x, player.x)
            for x in range(min_x + 1, max_x):
                if grid[self.y][x]:  # true if there is a wall
                    return False
            return True

        return False

    def shoot_arrow(
        self, player: Player, mape: Mape
    ) -> None:
        """
        shoots an arrow only if hardcore mode is active
        creature is alive and has line of sight
        """
        if not self.is_hardcore or not self.live:
            return

        if len(self.active_arrows) > 0:
            return

        if self.has_line_of_sight(player, mape):
            arrow = Arrow((self.x, self.y), self.direction)
            self.active_arrows.append(arrow)

    def move(self) -> None:
        pass

    def draw(self) -> None:
        pass

    def follow(self, player: Player) -> None:
        if self.live:
            self.target_point = (player.x, player.y)
        else:
            self.target_point = self.spawn_point


class Enderman(Monster):

    def __init__(
        self, spawn_point: tuple[int, int], is_hardcore: bool = False
    ) -> None:
        super().__init__(spawn_point, is_hardcore)
        self.teleport_cooldown: float = 20.0  # every 20 seconds
        self.current_pearl: EnderPearl | None = None

    def throw_pearl_and_teleport(self, maze_bounds: tuple[int, int]) -> None:
        """
        teleports the enderman using an enderpearl
        if alive and in hardcore mode
        """
        if not self.is_hardcore or not self.live:
            return

        rand_x = random.randint(0, maze_bounds[0])
        rand_y = random.randint(0, maze_bounds[1])

        self.current_pearl = EnderPearl((rand_x, rand_y))
        self.x = rand_x
        self.y = rand_y

    def move(self) -> None:
        pass

    def draw(self) -> None:
        pass

    def follow(self, player: Player) -> None:
        if self.live:
            self.target_point = (player.x, player.y)
        else:
            self.target_point = self.spawn_point


class Witch(Monster):

    def __init__(
        self, spawn_point: tuple[int, int], is_hardcore: bool = False
    ) -> None:
        super().__init__(spawn_point, is_hardcore)
        self.potion_cooldown: float = 30.0  # cooldown in seconds
        self.radius_check: int = 5  # 5-block radius

    def throw_slow_potion(self, player: Player) -> None:
        """
        throws a slow potion if player is within radius
        witch is alive, and in hardcore mode
        """
        if not self.is_hardcore or not self.live:
            return

        distance = math.sqrt(
            (self.x - player.x) ** 2 + (self.y - player.y) ** 2
        )
        if distance <= self.radius_check:
            potion = SlowPotion((self.x, self.y), duration=5)
            potion.apply_effect(player)

    def move(self) -> None:
        pass

    def draw(self) -> None:
        pass

    def follow(self, player: Player) -> None:
        if self.live:
            self.target_point = (player.x, player.y)
        else:
            self.target_point = self.spawn_point
