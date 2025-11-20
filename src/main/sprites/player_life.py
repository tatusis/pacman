# player_life.py

import pygame
from util.config import Config
from util.tileset import Tileset


class PlayerLife(pygame.sprite.Sprite):
    """Define the PlayerLife class"""

    def __init__(self, screen: pygame.surface.Surface, settings: Config, life: int) -> None:
        """Instantiates the PlayerLife class"""
        super().__init__()
        self.screen = screen
        self.settings = settings
        self.life = life

        tileset = Tileset(self.settings)

        self.image = tileset.get_tile(8, 1)
        self.rect = self.image.get_rect()

        if life == 0:
            self.rect.right = round((2 / 12) * self.settings.screen_width)
            self.rect.y = round((2 / 12) * self.settings.screen_height)
        elif life == 1:
            self.rect.right = round((2 / 12) * self.settings.screen_width)
            self.rect.y = round((2 / 12) * self.settings.screen_height) + 20
        elif life == 2:
            self.rect.right = round((2 / 12) * self.settings.screen_width)
            self.rect.y = round((2 / 12) * self.settings.screen_height) + 40
