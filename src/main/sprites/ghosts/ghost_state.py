# scene_state.py

from enum import Enum


class GhostState(Enum):
    """Defines the GhostState class"""

    NONE = 0
    WANDERING = 1
    CHASING = 2
    EVADING = 3
