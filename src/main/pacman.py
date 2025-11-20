# pacman.py

import json

import pygame
from pygame.locals import FULLSCREEN, QUIT, SCALED
from scenes.main_scene import MainScene
from scenes.menu_scene import MenuScene
from scenes.scene import Scene
from util.config import Config


class Pacman:
    """Defines the Pacman class"""

    def __init__(self) -> None:
        """Instantiates Pacman class"""
        with open("config/settings.json", "r") as file:
            self.settings = Config(**json.load(file))

        pygame.mixer.pre_init(
            self.settings.mixer_frequency,
            self.settings.mixer_size,
            self.settings.mixer_channels,
            self.settings.mixer_buffer,
        )
        pygame.init()
        flags = SCALED | FULLSCREEN
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height), flags)
        # self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        pygame.mouse.set_visible(False)
        pygame.event.set_allowed([QUIT])
        self.switch_scene(Scene.MENU_SCENE)
        self.clock = pygame.time.Clock()
        self.level = 1
        self.running = True

    def run(self) -> None:
        """Runs an instance of the Pacman class"""
        while self.running:
            dt = self.clock.tick(self.settings.game_fps) / 1000.0
            self.scene.handle_events()
            self.scene.update(dt)
            self.scene.draw()

            if self.scene.next_scene_name != self.scene_name:
                scene_name = self.scene.next_scene_name
                self.scene.next_scene_name = self.scene.scene_name
                self.switch_scene(scene_name)

        pygame.quit()

    def switch_scene(self, scene_name: Scene) -> None:
        """Switches the active scene"""
        self.scene_name = scene_name

        if self.scene_name == Scene.MENU_SCENE:
            self.scene = MenuScene(self.screen, self.settings)
        elif self.scene_name == Scene.MAIN_SCENE:
            self.scene = MainScene(self.screen, self.settings)
            self.scene.setup_level(self.level)
        elif self.scene_name == Scene.EXIT_SCENE:
            self.running = False


if __name__ == "__main__":
    Pacman().run()
