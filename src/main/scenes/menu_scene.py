# menu_scene.py

import pygame
from scenes.scene import Scene
from scenes.scene_state import SceneState
from util.config import Config


class MenuScene:
    """Defines the MenuScene class"""

    def __init__(self, screen: pygame.surface.Surface, settings: Config) -> None:
        """Instantiates the MenuScene class"""
        self.settings = settings
        self.screen = screen

        # Scene
        self.scene_name = Scene.MENU_SCENE
        self.next_scene_name = Scene.MENU_SCENE
        self.scene_state = SceneState.RUNNING

        # Music
        pygame.mixer.music.load(self.settings.menu_background_music)
        pygame.mixer.music.set_volume(self.settings.music_volume)
        pygame.mixer.music.play(-1)

        # Sound
        self.option_sound = pygame.mixer.Sound(self.settings.menu_option_sound)

        # Channels
        self.channel = pygame.mixer.Channel(0)
        self.channel.set_volume(self.settings.sound_volume)

        # Title
        self.title_font = pygame.font.Font(self.settings.menu_title_font_family, self.settings.menu_title_font_size)
        self.title_text = self.render_text(
            self.settings.menu_title_text, self.title_font, self.settings.menu_title_text_color
        )

        # Options
        self.option_font = pygame.font.Font(self.settings.menu_option_font_family, self.settings.menu_option_font_size)
        self.start_text = self.render_text(
            self.settings.menu_option_start_text, self.option_font, self.settings.menu_option_text_color
        )
        self.exit_text = self.render_text(
            self.settings.menu_option_exit_text, self.option_font, self.settings.menu_option_text_color
        )

    def handle_events(self) -> None:
        """Handles the MenuScene events"""
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.handle_start_option()
                elif event.key == pygame.K_ESCAPE:
                    self.handle_exit_option()

    def update(self, dt: float) -> None:
        """Handles the MenuScene logic"""
        pass

    def draw(self) -> None:
        """Renders the MenuScene to the screen"""
        self.screen.fill(self.settings.screen_color)
        self.display_text(self.title_text, (6 / 12), (4 / 12))
        self.display_text(self.start_text, (6 / 12), (7 / 12))
        self.display_text(self.exit_text, (6 / 12), (8 / 12))

        pygame.display.flip()

    def render_text(self, text: str, font: pygame.font.Font, color: str) -> pygame.surface.Surface:
        """Renders the texts"""
        return font.render(text, True, color)

    def display_text(self, text: pygame.surface.Surface, x: float, y: float) -> None:
        """Displays the texts"""
        rect = text.get_rect()
        rect.centerx = round(self.screen.get_rect().width * x)
        rect.centery = round(self.screen.get_rect().height * y)
        self.screen.blit(text, rect)

    def handle_start_option(self) -> None:
        """Handles the start option"""
        pygame.mixer.music.stop()
        self.channel.play(self.option_sound)

        while self.channel.get_busy():
            pygame.time.delay(10)
            pygame.event.poll()

        self.next_scene_name = Scene.MAIN_SCENE

    def handle_exit_option(self) -> None:
        """Handles the exit option"""
        self.next_scene_name = Scene.EXIT_SCENE
