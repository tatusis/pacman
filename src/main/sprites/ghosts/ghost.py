# ghost.py

import random

import pygame
from sprites.ghosts.ghost_state import GhostState
from sprites.ghosts.ghost_type import GhostType
from util.config import Config
from util.direction import Direction
from util.tileset import Tileset


class Ghost(pygame.sprite.Sprite):
    """Defines the Ghost class"""

    def __init__(self, *groups) -> None:
        """Instantiates the Ghost class"""
        super().__init__(*groups)

    def configure(
        self, screen: pygame.surface.Surface, settings: Config, x: int, y: int, seed: float, ghost_type: GhostType
    ) -> None:
        """Configures the Ghost class"""
        self.screen = screen
        self.settings = settings
        self.ghost_type = ghost_type

        # Ghost type
        if self.ghost_type == GhostType.BLINKY:
            index = 4
            self._layer = 9
            self.original_cooldown = 2
            self.cooldown = 2
        elif self.ghost_type == GhostType.PINKY:
            index = 5
            self._layer = 8
            self.original_cooldown = 6
            self.cooldown = 6
        elif self.ghost_type == GhostType.INKY:
            index = 6
            self._layer = 7
            self.original_cooldown = 10
            self.cooldown = 10
        elif self.ghost_type == GhostType.CLYDE:
            index = 7
            self._layer = 6
            self.original_cooldown = 16
            self.cooldown = 16

        tileset = Tileset(self.settings)

        # Up
        self.up_images = [
            tileset.get_tile(4, index),
            tileset.get_tile(5, index),
        ]

        # Right
        self.right_images = [
            tileset.get_tile(0, index),
            tileset.get_tile(1, index),
        ]

        # Down
        self.down_images = [
            tileset.get_tile(6, index),
            tileset.get_tile(7, index),
        ]

        # Left
        self.left_images = [
            tileset.get_tile(2, index),
            tileset.get_tile(3, index),
        ]

        self.evading_images = [
            tileset.get_tile(8, 4),
            tileset.get_tile(9, 4),
            tileset.get_tile(10, 4),
            tileset.get_tile(11, 4),
        ]

        self.animation_step = self.settings.ghost_animation_step
        self.image_index = 0
        self.image = self.right_images[self.image_index]
        self.rect = self.image.get_rect()
        self.radius = 10
        self.original_x = x
        self.original_y = y
        self.rect.x = self.original_x
        self.rect.y = self.original_y
        self.direction = Direction.NONE
        self.next_direction = Direction.NONE
        self.x_change = 0.0
        self.y_change = 0.0
        self.ghost_state = GhostState.NONE
        self.random = random.Random()
        self.random.seed(seed)
        self.wandering_point = tuple()
        self.returning = False

    def update(self, dt: float) -> None:
        """Handles the Ghost logic"""
        if self.cooldown > 0:
            self.cooldown -= dt
        else:
            self.handle_direction(dt)
            self.handle_teleport()

        self.handle_animation(dt)

    def handle_direction(self, dt: float) -> None:
        """Handles Ghost direction"""
        if self.direction == Direction.UP:
            self.y_change -= self.settings.ghost_speed * dt
        elif self.direction == Direction.RIGHT:
            self.x_change += self.settings.ghost_speed * dt
        elif self.direction == Direction.DOWN:
            self.y_change += self.settings.ghost_speed * dt
        elif self.direction == Direction.LEFT:
            self.x_change -= self.settings.ghost_speed * dt

        if abs(self.x_change) >= 1.0:
            self.rect.x += round(self.x_change)
            self.x_change = 0.0
        elif abs(self.y_change) >= 1.0:
            self.rect.y += round(self.y_change)
            self.y_change = 0.0

    def handle_teleport(self) -> None:
        """Handles Ghost teleport"""
        if self.rect.centerx > self.settings.screen_width - (
            self.settings.maze_left_margin + (self.settings.tile_size // 2)
        ):
            self.rect.centerx = self.settings.maze_left_margin + (self.settings.tile_size // 2)
        elif self.rect.centerx < self.settings.maze_left_margin + (self.settings.tile_size // 2):
            self.rect.centerx = self.settings.screen_width - (
                self.settings.maze_left_margin + (self.settings.tile_size // 2)
            )

    def handle_animation(self, dt: float) -> None:
        """Handles Ghost animation"""
        if self.ghost_state != GhostState.EVADING:
            if self.direction != Direction.NONE:
                if self.animation_step < 0:
                    self.image_index += 1

                    if self.image_index > 1:
                        self.image_index = 0

                    if self.direction == Direction.UP:
                        self.image = self.up_images[self.image_index]
                    elif self.direction == Direction.RIGHT:
                        self.image = self.right_images[self.image_index]
                    elif self.direction == Direction.DOWN:
                        self.image = self.down_images[self.image_index]
                    elif self.direction == Direction.LEFT:
                        self.image = self.left_images[self.image_index]

                    self.animation_step = self.settings.ghost_animation_step
                else:
                    self.animation_step -= dt
        else:
            if self.animation_step < 0:
                self.image_index += 1

                if self.image_index > 1 and self.returning == False:
                    self.image_index = 0

                if self.image_index > 3 and self.returning == True:
                    self.image_index = 0

                self.image = self.evading_images[self.image_index]
                self.animation_step = self.settings.ghost_animation_step
            else:
                self.animation_step -= dt
