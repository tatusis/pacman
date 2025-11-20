# scene_state.py

from enum import Enum


class SceneState(Enum):
    """Defines the SceneState class"""

    RUNNING = 0
    PAUSED = 1
    SUSPENDED = 2
    LEVEL_UP = 3
    GAME_OVER = 4
    HIT_STOP = 5
