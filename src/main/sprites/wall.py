# wall.py

import pygame


class Wall(pygame.sprite.Sprite):
    """Defines the Wall class"""

    def __init__(self, x: int, y: int, image: pygame.surface.Surface) -> None:
        """Instantiates the Wall class"""
        super().__init__()
        self._layer = 1
        self.image = image
        self.rect = image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, dt: float) -> None:
        """Handles the Wall logic"""
        pass
