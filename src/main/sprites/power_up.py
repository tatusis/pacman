# power_up.py

import pygame


class PowerUp(pygame.sprite.Sprite):
    """Defines the PowerUp class"""

    def __init__(self, x: int, y: int, image: pygame.surface.Surface) -> None:
        """Instantiates the PowerUp class"""
        super().__init__()
        self._layer = 1
        self.image = image
        self.rect = image.get_rect()
        self.radius = 2
        self.rect.x = x + 1
        self.rect.y = y

    def update(self, dt: float) -> None:
        """Handles the PowerUp logic"""
        pass
