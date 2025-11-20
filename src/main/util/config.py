# config.py

from dataclasses import dataclass


@dataclass
class Config:
    """Defines the Config class"""

    # Mixer
    mixer_frequency: int
    mixer_size: int
    mixer_channels: int
    mixer_buffer: int

    # Sound
    sound_volume: float

    # Music
    music_volume: float

    # Screen
    screen_width: int
    screen_height: int
    screen_color: str

    # Maze
    maze_size: int
    maze_left_margin: int
    maze_top_margin: int

    # Menu
    menu_title_font_family: str
    menu_title_font_size: int
    menu_title_text_color: str
    menu_title_text: str
    menu_option_font_family: str
    menu_option_font_size: int
    menu_option_text_color: str
    menu_option_start_text: str
    menu_option_exit_text: str
    menu_background_music: str
    menu_option_sound: str

    # Main
    main_font_family: str
    main_font_size: int
    main_text_color: str
    main_paused_text: str
    main_score_text: str
    main_high_score_text: str
    main_chomp_sound: str
    main_power_up_sound: str
    main_chase_sound: str
    main_death_sound: str
    main_pellet_score: int
    main_power_up_score: int

    game_fps: float
    tileset_path: str
    tile_size: int

    # Player
    player_speed: int
    player_animation_step: float
    player_up_images: list[list]
    player_right_images: list[list]
    player_down_images: list[list]
    player_left_images: list[list]
    player_death_images: list[list]

    # Ghost
    ghost_speed: int
    ghost_animation_step: float
    ghost_sensibility: int
