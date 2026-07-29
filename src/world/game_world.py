import random

import pygame

from src.building.ladder import Ladder
from src.building.lake import Lake
from src.entities.artifact import Artifact
from src.building.platform import Platform
from src.entities.player import Player
from src.entities.witch import Witch
from src.entities.little_enemy import LittleEnemy
from src.world import collision
from src.utils.config import GROUND_Y, SCREEN_H, SCREEN_W, WORLD_WIDTH, P_HEIGHT, P_WIDTH


class GameWorld:
    def __init__(self):
        self.platforms = self._build_platforms()
        # self.ladders   = self._build_ladders()
        self.ladders   = []
        self.artifacts = self._build_artifacts()
        self.player    = self._build_player()
        self.camera_x  = 0.0
        self.player_spawn = self.player.pos.copy()
        self.death_y = 465
        self.debug = False

        self.active_objects = []
        self.game_over = False
        self.lake = self._build_lake()

        self.active_objects.extend(self.artifacts)
        self.active_objects.append(self.player)

        self.enemies = self._spawn_enemies()
        self.active_objects.extend(self.enemies)

    def _spawn_enemies(self):
        ground_y = 400 - P_HEIGHT
        enemies = [
        Witch(pygame.Vector2(400, ground_y)),
        LittleEnemy(pygame.Vector2(900, ground_y)),
        Witch(pygame.Vector2(1600, ground_y)),
        LittleEnemy(pygame.Vector2(2500, ground_y)),
        ]
        return enemies

    def _build_platforms(self):
        platforms = []
        ground_y  = 400

        ground_segments = [
            (0,    500),
            (900,    2000),
            # (2100, 1800),
            # (4000, 2000),
        ]
        for start_x, width in ground_segments:
            platforms.append(Platform(pygame.Vector2(start_x, ground_y), width, 80))

        floating = [
            (*self.generate_random_positions(), 120),
            # (*self.generate_random_positions(), 100),
            (*self.generate_random_positions(), 130),
            (*self.generate_random_positions(), 110),
            (*self.generate_random_positions(), 110),
            (150, 256, 30),
            # (250, 56, 110),
        ]
        for x, y, w in floating:
            platforms.append(Platform(pygame.Vector2(x, y), w, 28))

        return platforms    

    def _build_player(self):
        return Player(pygame.Vector2(60, 400 - P_HEIGHT))
    
    def _build_artifacts(self):
        return [
            Artifact("Excalibur", "power", pygame.Vector2(587, 240)),
            Artifact("Santo Graal", "healing", pygame.Vector2(self.generate_random_positions())),
            Artifact("Cajado de Merlim", "magic", pygame.Vector2(self.generate_random_positions())),
        ]
    
    def _build_lake(self):
        return Lake(pygame.Vector2(500 , 400), 400, 100)

    def _update_camera(self):
        target = self.player.pos.x - SCREEN_W // 2
        self.camera_x += (target - self.camera_x) * 0.15
        self.camera_x = max(0, min(self.camera_x, WORLD_WIDTH - SCREEN_W))

    def handle_event(self, event):
        for obj in self.active_objects:
            if obj.active:
                obj.handle_event(event, self)

    def _collect_artifacts(self):
        collision.collect_artifacts(self.player, self.artifacts, self.active_objects)

    def update(self, dt):
        if self.game_over:
            # self.player.update_common(dt)
            # self.player._update_animation(dt)
            return

        for artifact in self.artifacts:
            collision.snap_to_platform(artifact, self.platforms)

        collision.collect_artifacts(self.player, self.artifacts, self.active_objects)

        lad_id = collision.get_ladder_hit(self.player, self.ladders)
        self.player.handle_input()
        self.player.update_common(dt)
        if lad_id != -1:
            on_ladder = collision.handle_ladder(self.player, self.platforms, dt, P_WIDTH * 0.9)
            if not on_ladder:
                collision.apply_gravity(self.player, dt)
                collision.move_with_platforms(self.player, self.platforms, dt)
        elif self.lake.in_lake_zone(self.player.rect):
            collision.handle_lake(self.player, self.lake, dt)
        else:
            collision.apply_gravity(self.player, dt)
            collision.move_with_platforms(self.player, self.platforms, dt)
        self.player._logic_state_machine()
        self.player._update_animation(dt)

        collision.apply_player_attack(self.player, self.enemies)

        for enemy in self.enemies:
            enemy.update(dt, self.platforms, self.player)

        if self.player.pos.x < 0:
            self.player.pos.x = 0
        elif self.player.pos.x > WORLD_WIDTH - P_WIDTH:
            self.player.pos.x = WORLD_WIDTH - P_WIDTH

        if not self.player.is_alive:
            self.game_over = True

        if self.player.pos.y > self.death_y:
            if self.player.take_damage(1, ignore_invuln=True):
                if not self.player.is_alive:
                    self.game_over = True
                else:
                    self.player.respawn(self.player_spawn)
        self._update_camera()   

    def draw(self, surface):
        cam = int(self.camera_x)
        for plat in self.platforms:
            plat.draw(surface, cam)
            if(plat.rect.top <= 305):
                height = (plat.rect.top - 280) * -1
                height = height if height > 50 else 50 
                plat_lad = Ladder(pygame.Vector2(plat.rect.left -32, plat.rect.top), 32, height)
                plat_lad.draw(surface, cam)
                self.ladders.append(plat_lad)
        
        for ladder in self.ladders:
            ladder.draw(surface, cam)

        self.lake.draw(surface, cam)
        if self.debug:
            pygame.draw.rect(surface, (0, 255, 255), self.lake.rect.move(-cam, 0), 2)

        # pygame.draw.rect(surface, (255, 0, 0), pygame.Rect(self.rect.left + 4, self.rect.top, self.rect.width - 8, self.rect.height), 1)
        
        for obj in self.active_objects:
            if obj.active:
                obj.draw(surface, cam)
                if self.debug:
                    pygame.draw.rect(surface, (0, 255, 255), obj.rect.move(-cam, 0), 2)
                    pygame.draw.rect(surface, (255, 0, 0), pygame.Rect(obj.rect.left + 4, obj.rect.top, obj.rect.width - 8, obj.rect.height).move(-cam, 0), 1)

        for i, artifact in enumerate(self.player.artifacts):
            artifact.pos.x = 10 + i * 30
            artifact.pos.y = 55
            artifact.draw(surface, 0)
        
    def get_artifact_info(self):
        if self.player.artifacts:
            return "Artifacts: "
        return "No artifacts collected"

    def generate_random_positions(self):
        x = random.randint(P_WIDTH, WORLD_WIDTH - P_WIDTH)
        y = random.randint(SCREEN_H - GROUND_Y , 360)
        return x, y
