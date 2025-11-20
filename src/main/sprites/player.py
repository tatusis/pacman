# player.py

import pygame
from sprites.ghosts.ghost import Ghost
from util.config import Config
from util.direction import Direction
from util.event import Event
from util.tileset import Tileset


class Player(pygame.sprite.Sprite):
    """Defines the Player class"""

    def __init__(self, *groups) -> None:
        """Instantiates the Player class"""
        super().__init__(*groups)
        self.up_images = []
        self.right_images = []
        self.down_images = []
        self.left_images = []
        self.death_images = []

    def configure(self, screen: pygame.surface.Surface, settings: Config, x: int, y: int) -> None:
        """Configures the Player class"""
        self.screen = screen
        self.settings = settings
        self._layer = 5

        tileset = Tileset(self.settings)

        # Up images
        for up_image in self.settings.player_up_images:
            self.up_images.append(tileset.get_tile(*up_image))

        # Right images
        for right_image in self.settings.player_right_images:
            self.right_images.append(tileset.get_tile(*right_image))

        # Down images
        for down_image in self.settings.player_down_images:
            self.down_images.append(tileset.get_tile(*down_image))

        # Left images
        for left_image in self.settings.player_left_images:
            self.left_images.append(tileset.get_tile(*left_image))

        # Death
        for death_image in self.settings.player_death_images:
            self.death_images.append(tileset.get_tile(*death_image))

        self.animation_step = self.settings.player_animation_step
        self.image_index = 2
        self.image = self.right_images[self.image_index]
        self.rect = self.image.get_rect()
        self.radius = 5
        self.original_x = x
        self.original_y = y
        self.rect.x = self.original_x
        self.rect.y = self.original_y
        self.direction = Direction.NONE
        self.next_direction = Direction.NONE
        self.x_change = 0.0
        self.y_change = 0.0
        self.lives = 0

    def update(self, dt: float) -> None:
        """Handles the Player logic"""
        self.handle_direction(dt)
        self.handle_teleport()
        self.handle_animation(dt)

    def handle_direction(self, dt: float) -> None:
        """Handles the Player direction"""
        if self.direction == Direction.UP:
            self.y_change -= self.settings.player_speed * dt
        elif self.direction == Direction.RIGHT:
            self.x_change += self.settings.player_speed * dt
        elif self.direction == Direction.DOWN:
            self.y_change += self.settings.player_speed * dt
        elif self.direction == Direction.LEFT:
            self.x_change -= self.settings.player_speed * dt

        if abs(self.x_change) >= 1.0:
            self.rect.x += round(self.x_change)
            self.x_change = 0.0
        elif abs(self.y_change) >= 1.0:
            self.rect.y += round(self.y_change)
            self.y_change = 0.0

    def handle_teleport(self) -> None:
        """Handles the Player teleport"""
        if self.rect.centerx > self.settings.screen_width - (
            self.settings.maze_left_margin + (self.settings.tile_size / 2)
        ):
            self.rect.centerx = self.settings.maze_left_margin + (self.settings.tile_size // 2)
        elif self.rect.centerx < self.settings.maze_left_margin + (self.settings.tile_size // 2):
            self.rect.centerx = self.settings.screen_width - (
                self.settings.maze_left_margin + (self.settings.tile_size // 2)
            )

    def handle_animation(self, dt: float, death: bool = False, game_over: bool = False) -> None:
        if self.direction != Direction.NONE:
            if self.animation_step < 0:
                self.image_index += 1

                if self.image_index > 3:
                    self.image_index = 0

                if self.direction == Direction.UP:
                    self.image = self.up_images[self.image_index]
                elif self.direction == Direction.RIGHT:
                    self.image = self.right_images[self.image_index]
                elif self.direction == Direction.DOWN:
                    self.image = self.down_images[self.image_index]
                elif self.direction == Direction.LEFT:
                    self.image = self.left_images[self.image_index]

                self.animation_step = self.settings.player_animation_step
            else:
                self.animation_step -= dt
        else:
            if death:
                if self.animation_step < 0:
                    if self.image_index == 0:
                        self.collided_ghost.rect.x = -20
                        self.collided_ghost.rect.y = -20

                    self.image_index += 1

                    if self.image_index < 12:
                        self.image = self.death_images[self.image_index]
                        self.animation_step = 0.16
                    else:
                        if not game_over:
                            pygame.event.post(pygame.event.Event(Event.PLAYER_RETURNED.value))
                else:
                    self.animation_step -= dt

    def handle_death(self, collided_ghost: Ghost):
        """Handles the Player death"""
        self.collided_ghost = collided_ghost
        self.direction = Direction.NONE
        self.next_direction = Direction.NONE
        self.animation_step = 0.41
        self.image_index = 0
        self.image = self.death_images[self.image_index]
