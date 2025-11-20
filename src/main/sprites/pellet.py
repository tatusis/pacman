# pellet.py

import pygame


class Pellet(pygame.sprite.Sprite):
    """Defines the Pellet class"""

    def __init__(self, x: int, y: int, image: pygame.surface.Surface) -> None:
        """Instantiates the Pellet class"""
        super().__init__()
        self._layer = 1
        self.image = image
        self.rect = image.get_rect()
        self.radius = 2
        self.rect.x = x
        self.rect.y = y

    def update(self, dt: float) -> None:
        """Handles the Pellet logic"""
        pass
