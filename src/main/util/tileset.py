# tileset.py

import pygame
from util.config import Config


class Tileset:
    """Defines the TileSet class"""

    def __init__(self, settings: Config) -> None:
        """Instantiates the TileSet class"""
        self.settings = settings
        self.tile_set = pygame.image.load(self.settings.tileset_path).convert_alpha()

    def get_tile(self, x: int, y: int) -> pygame.surface.Surface:
        """Returns a tile from tileset"""
        rect = pygame.rect.Rect(
            self.settings.tile_size * x,
            self.settings.tile_size * y,
            self.settings.tile_size,
            self.settings.tile_size,
        )
        tile = pygame.surface.Surface((self.settings.tile_size, self.settings.tile_size), pygame.SRCALPHA)
        tile.blit(self.tile_set, (0, 0), rect)
        return tile
