# event.py

from enum import Enum

import pygame


class Event(Enum):
    GHOST_RETURNING = pygame.USEREVENT + 1
    GHOST_RETURNED = pygame.USEREVENT + 2
    PLAYER_RETURNED = pygame.USEREVENT + 3
    GAME_OVER = pygame.USEREVENT + 4
    LEVEL_UP = pygame.USEREVENT + 5
    GHOST_KILL = pygame.USEREVENT + 6
