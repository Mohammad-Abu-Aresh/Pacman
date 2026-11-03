from __future__ import annotations
from typing import TYPE_CHECKING, Sequence
import pygame
from .block import Block, Mape
from .creature.spawn_point import Netherite
from photos.loderimages import Images

if TYPE_CHECKING:
    from .creature.creature import Creature
    from .creature.spawn_point import pacgum


class WorldSprite(pygame.sprite.Sprite):
    def __init__(
        self, image: pygame.Surface, rect: pygame.Rect, depth: int
    ) -> None:
        """
        Store an image, rectangle, and logical ground-row depth.
        Keep image height separate from world ordering.
        made by: Mohammad Abu Aresh
        """
        super().__init__()
        self.image = image
        self.rect = rect
        self.depth = depth

    def sync(
        self,
        image: pygame.Surface,
        rect: pygame.Rect,
        depth: int,
        group: pygame.sprite.LayeredUpdates,
    ) -> None:
        """
        Refresh a moving object's image, rectangle, and ground-row depth.
        Change its layer only when it crosses into another depth row.
        made by: Mohammad Abu Aresh
        """
        self.image = image
        self.rect = rect
        if depth != self.depth:
            group.change_layer(self, depth)
            self.depth = depth


class WorldRenderer:
    def __init__(self) -> None:
        """
        Create the ordered sprite group and object lookup tables.
        Static wall sprites are rebuilt only when the maze changes.
        made by: Mohammad Abu Aresh
        """
        self._group: pygame.sprite.LayeredUpdates = (
            pygame.sprite.LayeredUpdates()
        )
        self._map: Mape | None = None
        self._actor_sprites: dict[int, WorldSprite] = {}
        self._collectible_sprites: dict[int, WorldSprite] = {}
        self._actor_ids: tuple[int, ...] = ()
        self._collectible_ids: tuple[int, ...] = ()

    def draw(
        self,
        mape: Mape,
        actors: Sequence[Creature],
        collectibles: Sequence[pacgum],
    ) -> None:
        """
        Draw walls, actors, and collectibles in ascending screen depth.
        Objects with larger screen-Y anchors are painted later.
        made by: Mohammad Abu Aresh
        """
        actor_ids = tuple(id(actor) for actor in actors)
        collectible_ids = tuple(id(item) for item in collectibles)
        if (
            self._map is not mape
            or self._actor_ids != actor_ids
            or self._collectible_ids != collectible_ids
        ):
            self._rebuild(mape, actors, collectibles)
        self._sync_actors(mape, actors)
        self._remove_eaten_collectibles(collectibles)
        self._group.draw(Images.screen)

    def _rebuild(
        self,
        mape: Mape,
        actors: Sequence[Creature],
        collectibles: Sequence[pacgum],
    ) -> None:
        """
        Recreate static wall and collectible sprites for a new maze.
        Register actor sprites in the same ordered world collection.
        made by: Mohammad Abu Aresh
        """
        self._group.empty()
        self._actor_sprites.clear()
        self._collectible_sprites.clear()
        self._add_walls(mape)
        self._add_collectibles(mape, collectibles)
        self._add_actors(mape, actors)
        self._map = mape
        self._actor_ids = tuple(id(actor) for actor in actors)
        self._collectible_ids = tuple(id(item) for item in collectibles)

    def _add_walls(self, mape: Mape) -> None:
        """
        Create one persistent sprite for every wall cell in the maze.
        Position each wall from the map origin without actor lookups.
        made by: Mohammad Abu Aresh
        """
        image = Images.wall_new
        for row_index, row in enumerate(mape.every_cell):
            for column_index, is_wall in enumerate(row):
                if not is_wall:
                    continue
                location = (
                    mape.origin_x + column_index * Block.size,
                    mape.origin_y + row_index * Block.size,
                )
                rect = image.get_rect(topleft=location)
                depth = self._depth_layer(mape, row_index)
                sprite = WorldSprite(image, rect, depth)
                self._group.add(sprite, layer=depth)

    def _add_collectibles(
        self, mape: Mape, collectibles: Sequence[pacgum]
    ) -> None:
        """
        Convert each uneaten pellet into a small transparent sprite.
        Add pellets to the same depth ordering as walls and creatures.
        made by: Mohammad Abu Aresh
        """
        for item in collectibles:
            if item.is_eaten:
                continue
            is_power = isinstance(item, Netherite)
            radius = max(Block.size // (3 if is_power else 6), 1)
            diameter = radius * 2 + 2
            image = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
            color = (255, 165, 0) if is_power else (255, 255, 255)
            pygame.draw.circle(image, color, (radius + 1, radius + 1), radius)
            shift = 20 if is_power else 15
            center_x = (
                mape.origin_x + item.x * Block.size
                + Block.size // 2 + shift
            )
            center_y = (
                mape.origin_y + item.y * Block.size
                + Block.size // 2 + shift
            )
            center = (int(center_x), int(center_y))
            rect = image.get_rect(center=center)
            depth = self._depth_layer(mape, item.y)
            sprite = WorldSprite(image, rect, depth)
            self._group.add(sprite, layer=depth)
            self._collectible_sprites[id(item)] = sprite

    def _add_actors(
        self, mape: Mape, actors: Sequence[Creature]
    ) -> None:
        """
        Register creature sprites using their existing image placement.
        Keep the sprite lookup separate from movement and AI objects.
        made by: Mohammad Abu Aresh
        """
        for actor in actors:
            rect = actor.get_render_rect(mape)
            depth = self._depth_layer(mape, actor.y)
            sprite = WorldSprite(actor.image, rect, depth)
            self._group.add(sprite, layer=depth)
            self._actor_sprites[id(actor)] = sprite

    def _sync_actors(
        self, mape: Mape, actors: Sequence[Creature]
    ) -> None:
        """
        Update actor sprites from their current positions and images.
        Reorder only when an actor crosses a depth layer.
        made by: Mohammad Abu Aresh
        """
        for actor in actors:
            sprite = self._actor_sprites[id(actor)]
            sprite.sync(
                actor.image,
                actor.get_render_rect(mape),
                self._depth_layer(mape, actor.y),
                self._group,
            )

    def _depth_layer(self, mape: Mape, y: float) -> int:
        """
        Convert world Y into a pixel-based screen depth layer.
        Smaller screen Y values are drawn before larger values.
        made by: Mohammad Abu Aresh
        """
        return round(mape.origin_y + y * Block.size)

    def _remove_eaten_collectibles(
        self, collectibles: Sequence[pacgum]
    ) -> None:
        """
        Remove consumed pellets from the ordered rendering collection.
        Leave all remaining world sprites in their existing layers.
        made by: Mohammad Abu Aresh
        """
        for item in collectibles:
            if not item.is_eaten:
                continue
            sprite = self._collectible_sprites.pop(id(item), None)
            if sprite is not None:
                self._group.remove(sprite)
