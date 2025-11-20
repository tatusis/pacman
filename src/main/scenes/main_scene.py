# main_scene.py

import random
import time
from typing import Optional

import numpy as np
import pygame
import pytmx
from pathfinding.core.grid import Grid, GridNode
from pathfinding.finder.a_star import AStarFinder
from scenes.scene import Scene
from scenes.scene_state import SceneState
from sprites.ghosts.ghost import Ghost
from sprites.ghosts.ghost_state import GhostState
from sprites.ghosts.ghost_type import GhostType
from sprites.pellet import Pellet
from sprites.player import Player
from sprites.player_life import PlayerLife
from sprites.power_up import PowerUp
from sprites.wall import Wall
from util.config import Config
from util.direction import Direction
from util.event import Event


class MainScene:
    """Defines the MainScene class"""

    def __init__(self, screen: pygame.surface.Surface, settings: Config) -> None:
        """Instantiates the MainScene class"""
        self.screen = screen
        self.settings = settings

        # Score
        self.score = 0
        self.high_score = 0

        # Tiled Map
        self.tmx_data = pytmx.load_pygame("resources/pacman.tmx")

        # Sounds
        self.chomp_sound = pygame.mixer.Sound(self.settings.main_chomp_sound)
        self.power_up_sound = pygame.mixer.Sound(self.settings.main_power_up_sound)
        self.chase_sound = pygame.mixer.Sound(self.settings.main_chase_sound)
        self.death_sound = pygame.mixer.Sound(self.settings.main_death_sound)
        self.next_level_sound = pygame.mixer.Sound("resources/next_level.mp3")
        self.kill_sound = pygame.mixer.Sound("resources/kill.mp3")

        # Channels
        self.channels: list[pygame.mixer.Channel] = []
        self.chomp_channel = pygame.mixer.Channel(0)
        self.chomp_channel.set_volume(self.settings.sound_volume)
        self.channels.append(self.chomp_channel)
        self.power_up_channel = pygame.mixer.Channel(1)
        self.power_up_channel.set_volume(self.settings.sound_volume)
        self.channels.append(self.power_up_channel)
        self.chase_channel = pygame.mixer.Channel(2)
        self.chase_channel.set_volume(self.settings.sound_volume)
        self.channels.append(self.chase_channel)
        self.death_channel = pygame.mixer.Channel(3)
        self.death_channel.set_volume(self.settings.sound_volume)
        self.channels.append(self.death_channel)
        self.next_level_channel = pygame.mixer.Channel(4)
        self.next_level_channel.set_volume(self.settings.sound_volume)
        self.channels.append(self.next_level_channel)
        self.kill_channel = pygame.mixer.Channel(5)
        self.kill_channel.set_volume(self.settings.sound_volume)
        self.channels.append(self.kill_channel)

    def setup_level(self, level: int, player_lives: int = 3):
        """Sets up the game level"""
        self.level = level
        self.settings.ghost_speed += 5

        # Scene
        self.scene_name = Scene.MAIN_SCENE
        self.next_scene_name = Scene.MAIN_SCENE
        self.scene_state = SceneState.RUNNING

        # Sprites group
        self.sprites = pygame.sprite.LayeredUpdates()
        self.walls = pygame.sprite.Group()
        self.pellets = pygame.sprite.Group()
        self.power_ups = pygame.sprite.Group()
        self.ghosts = pygame.sprite.Group()
        self.player_lifes = pygame.sprite.Group()
        self.finder = AStarFinder()

        # Maze array
        maze_array = np.ones((23, 23))

        # Walls
        layer = self.tmx_data.layernames["Walls"]

        for x, y, tile in layer.tiles():
            if tile:
                x_screen, y_screen = self.grid_to_screen(x, y)
                wall = Wall(x_screen, y_screen, tile)
                self.walls.add(wall)
                self.sprites.add(wall)
                maze_array[y, x] = 0

        # Maze grid
        self.maze_grid = Grid(matrix=maze_array)

        # Maze points
        points_y, points_x = np.where(maze_array == 1)
        self.maze_points = list(zip(points_x, points_y))

        for point in self.maze_points:
            if (point[0] == 0 and point[1] == 11) or (point[0] == 22 and point[1] == 11):
                self.maze_points.remove(point)

        for i in range(len(self.maze_points)):
            x = (self.maze_points[i][0] * self.settings.tile_size) + self.settings.maze_left_margin
            y = (self.maze_points[i][1] * self.settings.tile_size) + self.settings.maze_top_margin
            self.maze_points[i] = (x, y)

        # Pellets
        layer = self.tmx_data.layernames["Pellets"]

        for x, y, tile in layer.tiles():
            if tile:
                x_screen, y_screen = self.grid_to_screen(x, y)
                pellet = Pellet(x_screen, y_screen, tile)
                self.pellets.add(pellet)
                self.sprites.add(pellet)

        # Power-ups
        layer = self.tmx_data.layernames["PowerUps"]

        for x, y, tile in layer.tiles():
            if tile:
                x_screen, y_screen = self.grid_to_screen(x, y)
                power_up = PowerUp(x_screen, y_screen, tile)
                self.power_ups.add(power_up)
                self.sprites.add(power_up)

        # Player
        player_layer = self.tmx_data.layernames["Player"]

        for x, y, _ in player_layer.tiles():
            x_screen, y_screen = self.grid_to_screen(x, y)
            self.player = Player()
            self.player.configure(self.screen, self.settings, x_screen, y_screen)
            self.player.lives = player_lives
            self.sprites.add(self.player)

        # Player lives
        for i in range(self.player.lives):
            player_life = PlayerLife(self.screen, self.settings, i)
            self.player_lifes.add(player_life)
            self.sprites.add(player_life)

        # Ghosts
        random.seed(time.time())

        for ghost_type in GhostType:
            ghost_layer = self.tmx_data.layernames[ghost_type.name]

            for x, y, _ in ghost_layer.tiles():
                x_screen, y_screen = self.grid_to_screen(x, y)
                ghost = Ghost()
                ghost.configure(self.screen, self.settings, x_screen, y_screen, random.random(), ghost_type)
                self.ghosts.add(ghost)
                self.sprites.add(ghost)

        self.accumulator = 0.0
        self.time_step = 1.0 / (self.settings.game_fps * 1.0)

        # Font
        self.font = pygame.font.Font(self.settings.main_font_family, self.settings.main_font_size)

        # Level
        self.level_text = self.render_text(f"LEVEL {self.level}", self.font, self.settings.main_text_color)

        # Score
        self.score_text = self.render_text(self.settings.main_score_text, self.font, self.settings.main_text_color)
        self.score_value_text = self.render_text(str(self.score), self.font, self.settings.main_text_color)
        self.high_score_text = self.render_text(
            self.settings.main_high_score_text, self.font, self.settings.main_text_color
        )
        self.high_score_value_text = self.render_text(str(self.high_score), self.font, self.settings.main_text_color)

        # Paused
        self.paused_text = self.render_text(self.settings.main_paused_text, self.font, self.settings.main_text_color)

        # Game over
        self.game_over_text = self.render_text("GAME OVER", self.font, self.settings.main_text_color)

        # Level up
        self.level_up_text = self.render_text("LEVEL UP", self.font, self.settings.main_text_color)
        self.collided_ghost: Optional[Ghost] = None

    def handle_events(self) -> None:
        """Handles the MainScene events"""
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.scene_state == SceneState.PAUSED:
                        self.next_scene_name = Scene.MENU_SCENE
                    elif self.scene_state == SceneState.RUNNING:
                        self.stop_all_sound_channels()
                        self.scene_state = SceneState.PAUSED
                elif event.key == pygame.K_RETURN:
                    if self.scene_state == SceneState.PAUSED:
                        self.scene_state = SceneState.RUNNING

                if self.scene_state == SceneState.RUNNING:
                    if event.key == pygame.K_UP:
                        if self.player.direction != Direction.UP:
                            self.player.next_direction = Direction.UP
                    elif event.key == pygame.K_RIGHT:
                        if self.player.direction != Direction.RIGHT:
                            self.player.next_direction = Direction.RIGHT
                    elif event.key == pygame.K_DOWN:
                        if self.player.direction != Direction.DOWN:
                            self.player.next_direction = Direction.DOWN
                    elif event.key == pygame.K_LEFT:
                        if self.player.direction != Direction.LEFT:
                            self.player.next_direction = Direction.LEFT
            elif event.type == Event.GHOST_RETURNING.value:
                for ghost in self.ghosts:
                    ghost.returning = True
                pygame.time.set_timer(pygame.event.Event(Event.GHOST_RETURNING.value), 0)
                pygame.time.set_timer(pygame.event.Event(Event.GHOST_RETURNED.value), 2_500)
            elif event.type == Event.GHOST_RETURNED.value:
                for ghost in self.ghosts:
                    ghost.returning = False
                    ghost.ghost_state = GhostState.WANDERING
                pygame.time.set_timer(pygame.event.Event(Event.GHOST_RETURNED.value), 0)
            elif event.type == Event.PLAYER_RETURNED.value:
                self.player.animation_step = self.settings.player_animation_step
                self.player.image_index = 2
                self.player.image = self.player.right_images[self.player.image_index]
                self.player.rect.x = self.player.original_x
                self.player.rect.y = self.player.original_y

                for ghost in self.ghosts:
                    ghost.ghost_state = GhostState.NONE
                    ghost.cooldown = ghost.original_cooldown
                    ghost.rect.x = ghost.original_x
                    ghost.rect.y = ghost.original_y

                self.scene_state = SceneState.RUNNING
            elif event.type == Event.GAME_OVER.value:
                pygame.time.set_timer(pygame.event.Event(Event.GAME_OVER.value), 0)
                self.next_scene_name = Scene.MENU_SCENE
            elif event.type == Event.LEVEL_UP.value:
                pygame.time.set_timer(pygame.event.Event(Event.LEVEL_UP.value), 0)
                self.setup_level(self.level + 1, self.player.lives)
            elif event.type == Event.GHOST_KILL.value:
                pygame.time.set_timer(pygame.event.Event(Event.GHOST_KILL.value), 0)
                self.score += 200
                self.score_value_text = self.render_text(str(self.score), self.font, self.settings.main_text_color)

                if self.collided_ghost is not None:
                    self.collided_ghost.ghost_state = GhostState.NONE
                    self.collided_ghost.cooldown = 2
                    self.collided_ghost.rect.x = self.collided_ghost.original_x
                    self.collided_ghost.rect.y = self.collided_ghost.original_y
                    self.collided_ghost = None

                self.scene_state = SceneState.RUNNING

    def update(self, dt: float) -> None:
        """Handles the MainScene logic"""
        if self.scene_state == SceneState.RUNNING:
            self.accumulator += dt

            while self.accumulator >= self.time_step:
                self.sprites.update(self.time_step)
                self.accumulator -= self.time_step
                self.handle_collisions()
                self.handle_player_direction()

                for ghost in self.ghosts:
                    self.handle_ghost_state(ghost)
        elif self.scene_state == SceneState.SUSPENDED:
            self.player.handle_animation(dt, True)
        elif self.scene_state == SceneState.GAME_OVER:
            self.player.handle_animation(dt, True, True)

    def stop_all_sound_channels(self) -> None:
        """Stops all sound channels"""
        for channel in self.channels:
            channel.stop()

    def handle_ghost_state(self, ghost: Ghost) -> None:
        """Handles Ghost state"""
        start_node = self.get_node(ghost.rect.x, ghost.rect.y)
        end_node = self.get_node(self.player.rect.x, self.player.rect.y)
        path, _ = self.finder.find_path(start_node, end_node, self.maze_grid)

        if len(path) == 1:
            pass
        if len(path) > 1 and len(path) <= self.settings.ghost_sensibility and ghost.ghost_state != GhostState.EVADING:
            x_screen, y_screen = self.grid_to_screen(path[1].x, path[1].y)

            if ghost.ghost_state != GhostState.CHASING:
                ghost.ghost_state = GhostState.CHASING

            self.handle_ghost_direction(ghost, x_screen, y_screen)
        elif len(path) > 1 and len(path) <= self.settings.ghost_sensibility and ghost.ghost_state == GhostState.EVADING:
            if ghost.wandering_point == ():
                ghost.wandering_point = ghost.random.choice(self.maze_points)

            start_node = self.get_node(ghost.rect.x, ghost.rect.y)
            end_node = self.get_node(ghost.wandering_point[0], ghost.wandering_point[1])
            path, _ = self.finder.find_path(start_node, end_node, self.maze_grid)

            if len(path) == 1:
                ghost.wandering_point = tuple()
            elif len(path) > 1:
                x_screen, y_screen = self.grid_to_screen(path[1].x, path[1].y)
                self.handle_ghost_direction(ghost, x_screen, y_screen)
        elif len(path) > self.settings.ghost_sensibility and ghost.ghost_state == GhostState.EVADING:
            if ghost.wandering_point == ():
                ghost.wandering_point = ghost.random.choice(self.maze_points)

            start_node = self.get_node(ghost.rect.x, ghost.rect.y)
            end_node = self.get_node(ghost.wandering_point[0], ghost.wandering_point[1])
            path, _ = self.finder.find_path(start_node, end_node, self.maze_grid)

            if len(path) == 1:
                ghost.wandering_point = tuple()
            elif len(path) > 1:
                x_screen, y_screen = self.grid_to_screen(path[1].x, path[1].y)
                self.handle_ghost_direction(ghost, x_screen, y_screen)
        elif len(path) > self.settings.ghost_sensibility and ghost.ghost_state != GhostState.EVADING:
            if ghost.wandering_point == ():
                ghost.wandering_point = ghost.random.choice(self.maze_points)

            start_node = self.get_node(ghost.rect.x, ghost.rect.y)
            end_node = self.get_node(ghost.wandering_point[0], ghost.wandering_point[1])
            path, _ = self.finder.find_path(start_node, end_node, self.maze_grid)

            if len(path) == 1:
                ghost.wandering_point = tuple()
            elif len(path) > 1:
                x_screen, y_screen = self.grid_to_screen(path[1].x, path[1].y)

                if ghost.ghost_state != GhostState.WANDERING:
                    ghost.ghost_state = GhostState.WANDERING

                self.handle_ghost_direction(ghost, x_screen, y_screen)

    def handle_ghost_direction(self, ghost: Ghost, x: int, y: int) -> None:
        """Handles Ghost direction"""
        if ghost.rect.x == x:
            if ghost.rect.y > y:
                ghost.next_direction = Direction.UP
            elif ghost.rect.y < y:
                ghost.next_direction = Direction.DOWN
        elif ghost.rect.y == y:
            if ghost.rect.x > x:
                ghost.next_direction = Direction.LEFT
            elif ghost.rect.x < x:
                ghost.next_direction = Direction.RIGHT

        if ghost.next_direction != Direction.NONE:
            x = ghost.rect.x
            y = ghost.rect.y

            if ghost.next_direction == Direction.UP:
                ghost.rect.y -= 1
            elif ghost.next_direction == Direction.RIGHT:
                ghost.rect.x += 1
            elif ghost.next_direction == Direction.DOWN:
                ghost.rect.y += 1
            elif ghost.next_direction == Direction.LEFT:
                ghost.rect.x -= 1

            collided_wall_list: list[Wall] = pygame.sprite.spritecollide(ghost, self.walls, False)

            if len(collided_wall_list) == 0:
                ghost.direction = ghost.next_direction
                ghost.next_direction = Direction.NONE

            ghost.rect.x = x
            ghost.rect.y = y

    def handle_collisions(self) -> None:
        """Handles sprttes collisions"""

        # Ghosts collisions
        collided_ghosts_list: list[Ghost] = pygame.sprite.spritecollide(self.player, self.ghosts, False)

        if len(collided_ghosts_list) > 0:
            for collided_ghost in collided_ghosts_list:
                if pygame.sprite.collide_circle(self.player, collided_ghost):
                    if collided_ghost.ghost_state == GhostState.EVADING:
                        self.kill_channel.play(self.kill_sound)
                        self.scene_state = SceneState.HIT_STOP
                        self.collided_ghost = collided_ghost
                        pygame.time.set_timer(pygame.event.Event(Event.GHOST_KILL.value), 300)
                    else:
                        self.scene_state = SceneState.SUSPENDED
                        self.stop_all_sound_channels()
                        self.death_channel.play(self.death_sound)

                        if self.player.lives > 0:
                            player_life = self.player_lifes.sprites()[self.player.lives - 1]
                            self.player_lifes.remove(player_life)
                            self.sprites.remove(player_life)
                            self.player.lives -= 1

                        if self.player.lives == 0:
                            self.scene_state = SceneState.GAME_OVER
                            pygame.time.set_timer(pygame.event.Event(Event.GAME_OVER.value), 4_000)

                        for ghost in self.ghosts:
                            if ghost != collided_ghost:
                                ghost.rect.x = -20
                                ghost.rect.y = -20

                        self.player.handle_death(collided_ghost)

        # Pellets collisions
        collided_pellets_list: list[Wall] = pygame.sprite.spritecollide(self.player, self.pellets, False)

        if len(collided_pellets_list) > 0:
            for collided_pellet in collided_pellets_list:
                if pygame.sprite.collide_circle(self.player, collided_pellet):
                    self.pellets.remove(collided_pellet)
                    self.sprites.remove(collided_pellet)

                    if not self.chomp_channel.get_busy():
                        self.chomp_channel.play(self.chomp_sound)

                    self.score += self.settings.main_pellet_score
                    self.score_value_text = self.render_text(str(self.score), self.font, self.settings.main_text_color)

                    if len(self.pellets) == 0:
                        self.stop_all_sound_channels()
                        self.next_level_channel.play(self.next_level_sound)
                        self.scene_state = SceneState.LEVEL_UP
                        pygame.time.set_timer(pygame.event.Event(Event.LEVEL_UP.value), 2_500)

        # Power-ups collisions
        collided_power_ups_list: list[PowerUp] = pygame.sprite.spritecollide(self.player, self.power_ups, False)

        if len(collided_power_ups_list) > 0:
            for collided_power_up in collided_power_ups_list:
                if pygame.sprite.collide_circle(self.player, collided_power_up):
                    self.power_ups.remove(collided_power_up)
                    self.sprites.remove(collided_power_up)
                    self.power_up_channel.play(self.power_up_sound)

                    for ghost in self.ghosts:
                        ghost.returning = False
                        ghost.ghost_state = GhostState.EVADING

                    self.score += self.settings.main_power_up_score
                    self.score_value_text = self.render_text(str(self.score), self.font, self.settings.main_text_color)
                    pygame.time.set_timer(pygame.event.Event(Event.GHOST_RETURNING.value), 5_000)
                    pygame.time.set_timer(pygame.event.Event(Event.GHOST_RETURNED.value), 0)

        # Walls collisions
        collided_walls_list: list[Wall] = pygame.sprite.spritecollide(self.player, self.walls, False)

        if len(collided_walls_list) > 0:
            if self.player.direction == Direction.UP:
                self.player.rect.top = collided_walls_list[0].rect.bottom
            elif self.player.direction == Direction.RIGHT:
                self.player.rect.right = collided_walls_list[0].rect.left
            elif self.player.direction == Direction.DOWN:
                self.player.rect.bottom = collided_walls_list[0].rect.top
            elif self.player.direction == Direction.LEFT:
                self.player.rect.left = collided_walls_list[0].rect.right

            self.player.direction = Direction.NONE

        for ghost in self.ghosts:
            collided_walls_list: list[Wall] = pygame.sprite.spritecollide(ghost, self.walls, False)

            if len(collided_walls_list) > 0:
                if ghost.direction == Direction.UP:
                    ghost.rect.top = collided_walls_list[0].rect.bottom
                elif ghost.direction == Direction.RIGHT:
                    ghost.rect.right = collided_walls_list[0].rect.left
                elif ghost.direction == Direction.DOWN:
                    ghost.rect.bottom = collided_walls_list[0].rect.top
                elif ghost.direction == Direction.LEFT:
                    ghost.rect.left = collided_walls_list[0].rect.right

                ghost.direction = Direction.NONE

    def handle_player_direction(self) -> None:
        """Handles Player direction"""
        if self.player.next_direction != Direction.NONE:
            x = self.player.rect.x
            y = self.player.rect.y

            if self.player.next_direction == Direction.UP:
                self.player.rect.y -= 1
            elif self.player.next_direction == Direction.RIGHT:
                self.player.rect.x += 1
            elif self.player.next_direction == Direction.DOWN:
                self.player.rect.y += 1
            elif self.player.next_direction == Direction.LEFT:
                self.player.rect.x -= 1

            collided_wall_list: list[Wall] = pygame.sprite.spritecollide(self.player, self.walls, False)

            if len(collided_wall_list) == 0:
                self.player.direction = self.player.next_direction
                self.player.next_direction = Direction.NONE

            self.player.rect.x = x
            self.player.rect.y = y

    def draw(self) -> None:
        """Renders the MainScene to the screen"""
        self.screen.fill(pygame.color.THECOLORS[self.settings.screen_color])

        if self.scene_state == SceneState.PAUSED:
            self.display_text(self.paused_text, (10 / 12), (10 / 12))

        if self.scene_state == SceneState.GAME_OVER:
            self.display_text(self.game_over_text, (10 / 12), (10 / 12))

        if self.scene_state == SceneState.LEVEL_UP:
            self.display_text(self.level_up_text, (10 / 12), (10 / 12))

        self.display_text(self.level_text, (2 / 12), (1 / 12), "RIGHT")
        self.display_text(self.score_text, (10 / 12), (1 / 12))
        self.display_text(self.score_value_text, (10 / 12), (2 / 12))
        self.display_text(self.high_score_text, (10 / 12), (3 / 12))
        self.display_text(self.high_score_value_text, (10 / 12), (4 / 12))
        self.sprites.draw(self.screen)
        pygame.display.flip()

    def render_text(self, text: str, font: pygame.font.Font, color: str) -> pygame.surface.Surface:
        """Renders the texts"""
        return font.render(text, True, color)

    def display_text(self, text: pygame.surface.Surface, x: float, y: float, side: str = "LEFT") -> None:
        """Displays the texts"""
        rect = text.get_rect()

        if side == "LEFT":
            rect.left = round(self.screen.get_rect().width * x)
        elif side == "RIGHT":
            rect.right = round(self.screen.get_rect().width * x)

        rect.y = round(self.screen.get_rect().height * y)
        self.screen.blit(text, rect)

    def screen_to_grid(self, x_screen: int, y_screen: int) -> tuple[int, int]:
        """Transforms a coordinate from the screen to the grid"""
        x_grid = (x_screen - self.settings.maze_left_margin) // self.settings.tile_size
        y_grid = (y_screen - self.settings.maze_top_margin) // self.settings.tile_size
        return x_grid, y_grid

    def grid_to_screen(self, x_grid: int, y_grid: int) -> tuple[int, int]:
        """Transforms a grid coordinate onto the screen"""
        x_screen = (x_grid * self.settings.tile_size) + self.settings.maze_left_margin
        y_screen = (y_grid * self.settings.tile_size) + self.settings.maze_top_margin
        return x_screen, y_screen

    def get_node(self, x_screen: int, y_screen: int) -> GridNode:
        """Returns a grid node"""
        x_grid, y_grid = self.screen_to_grid(x_screen, y_screen)
        node = self.maze_grid.node(x_grid, y_grid)
        return node
