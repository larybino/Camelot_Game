import random
from pathlib import Path

import pygame

from src.building.ladder import Ladder
from src.building.lake import Lake
from src.entities.artifact import Artifact
from src.entities.coin import Coin
from src.building.platform import Platform
from src.entities.player import Player
from src.entities.witch import Witch
from src.entities.little_enemy import LittleEnemy
from src.world import collision
from src.utils.config import GROUND_Y, SCREEN_H, SCREEN_W, WORLD_WIDTH, P_HEIGHT, P_WIDTH


GROUND_EXTENSION_WIDTH = WORLD_WIDTH + 600
COLLECTIBLE_SPAWN_MAX_X = WORLD_WIDTH - 180
FINISH_MARGIN_X = 380


class GameWorld:
    def __init__(self):
        self.platforms = self._build_platforms()
        self.ladders = self._build_ladders()
        self.artifacts = self._build_artifacts()
        self.coins = self._build_coins()
        self.player    = self._build_player()
        self.camera_x  = 0.0
        self.player_spawn = self.player.pos.copy()
        self.death_y = 465
        self.debug = False
        self.score = 0

        self.active_objects = []
        self.game_over = False
        self.game_won = False
        self.lake = self._build_lake()
        self._sfx = self._load_sfx()
        self._rewarded_enemy_ids = set()
        self._last_player_lives = self.player.lives
        self._victory_sound_played = False
        self._applied_artifact_effects = set()
        self._pickup_fx_timer = 0.0
        self._pickup_fx_color = (255, 255, 255)

        self.active_objects.extend(self.artifacts)
        self.active_objects.extend(self.coins)
        self.active_objects.append(self.player)

        self.enemies = self._spawn_enemies()
        self.active_objects.extend(self.enemies)
        self._randomize_collectibles_on_platforms()
        self.world_end_x = self._compute_world_end_x()

    def _load_sfx(self):
        root = Path(__file__).resolve().parents[2]
        sfx_dir = root / "assets" / "sprites" / "brackeys_platformer_assets" / "sounds"
        mapping = {
            "coin": "coin.wav",
            "artifact": "power_up.wav",
            "attack": "tap.wav",
            "hurt": "hurt.wav",
            "enemy_down": "explosion.wav",
            "victory": "power_up.wav",
        }
        loaded = {}
        for key, filename in mapping.items():
            path = sfx_dir / filename
            if not path.exists():
                loaded[key] = None
                continue
            try:
                loaded[key] = pygame.mixer.Sound(str(path))
            except pygame.error:
                loaded[key] = None
        return loaded

    def _play_sfx(self, key):
        sound = self._sfx.get(key)
        if sound:
            sound.play()

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
            (0, GROUND_EXTENSION_WIDTH),
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
            Artifact("Excalibur", "power", pygame.Vector2(0, 0)),
            Artifact("Santo Graal", "healing", pygame.Vector2(0, 0)),
            Artifact("Cajado de Merlim", "magic", pygame.Vector2(0, 0)),
        ]

    def _build_coins(self):
        return [Coin(pygame.Vector2(0, 0)) for _ in range(8)]
    
    def _build_lake(self):
        return Lake(pygame.Vector2(500 , 400), 400, 100)

    def _build_ladders(self):
        ladders = []
        for plat in self.platforms:
            if plat.rect.top <= 305:
                height = max(50, (plat.rect.top - 280) * -1)
                ladders.append(Ladder(pygame.Vector2(plat.rect.left - 32, plat.rect.top), 32, height))
        return ladders

    def _pick_collectible_spot(self, obj_width, obj_height, used_spots):
        candidates = [
            p for p in self.platforms
            if p.width >= obj_width + 8 and p.rect.left <= COLLECTIBLE_SPAWN_MAX_X
        ]
        if not candidates:
            return P_WIDTH, GROUND_Y - obj_height

        for _ in range(40):
            plat = random.choice(candidates)
            min_x = plat.rect.left
            max_x = min(plat.rect.right - obj_width, COLLECTIBLE_SPAWN_MAX_X - obj_width)
            if max_x < min_x:
                continue

            x = random.randint(min_x, max_x)
            y = plat.rect.top - obj_height

            if all(abs(x - px) >= 28 or abs(y - py) >= 16 for px, py in used_spots):
                return x, y

        fallback = random.choice(candidates)
        fallback_x = min(fallback.rect.left, COLLECTIBLE_SPAWN_MAX_X - obj_width)
        return fallback_x, fallback.rect.top - obj_height

    def _randomize_collectibles_on_platforms(self):
        used_spots = []

        for artifact in self.artifacts:
            x, y = self._pick_collectible_spot(artifact.width, artifact.height, used_spots)
            artifact.pos.x = x
            artifact.pos.y = y
            used_spots.append((x, y))

        for coin in self.coins:
            x, y = self._pick_collectible_spot(coin.width, coin.height, used_spots)
            coin.pos.x = x
            coin.pos.y = y
            used_spots.append((x, y))

    def _compute_world_end_x(self):
        collectible_positions = [obj.pos.x for obj in (self.artifacts + self.coins)]
        if not collectible_positions:
            return WORLD_WIDTH

        farthest_collectible_x = max(collectible_positions)
        target_end = int(farthest_collectible_x + FINISH_MARGIN_X)
        return max(SCREEN_W + 200, min(target_end, WORLD_WIDTH))

    def _update_camera(self):
        target = self.player.pos.x - SCREEN_W // 2
        self.camera_x += (target - self.camera_x) * 0.15
        world_right = self._get_world_right_bound()
        self.camera_x = max(0, min(self.camera_x, world_right - SCREEN_W))

    def _get_world_right_bound(self):
        return self.world_end_x

    def handle_event(self, event):
        for obj in self.active_objects:
            if obj.active:
                obj.handle_event(event, self)

    def _collect_artifacts(self):
        collision.collect_artifacts(self.player, self.artifacts, self.active_objects)

    def _is_victory(self):
        if self.game_over:
            return False
        return len(self.player.artifacts) >= 2 and self.player.is_alive

    def _apply_artifact_effect(self, artifact):
        name = artifact.name
        if name in self._applied_artifact_effects:
            return

        if name == "Santo Graal":
            if self.player.lives == self.player.max_lives and self.player.max_lives < 5:
                self.player.max_lives += 1
            self.player.lives = min(self.player.max_lives, self.player.lives + 1)
            self._pickup_fx_color = (210, 255, 210)

        elif name == "Excalibur":
            self.player.attack_damage += 2
            self.player.attack_range_x += 20
            self._pickup_fx_color = (255, 225, 120)

        elif name == "Cajado de Merlim":
            self.player.attack_range_x += 45
            self.player.attack_range_y += 20
            self.player.attack_interval = max(0.16, self.player.attack_interval * 0.6)
            self.player.attack_cooldown = min(self.player.attack_cooldown, self.player.attack_interval)
            self._pickup_fx_color = (180, 220, 255)

        self._pickup_fx_timer = 0.45
        self._applied_artifact_effects.add(name)

    def update(self, dt):
        if self.game_over or self.game_won:
            # self.player.update_common(dt)
            # self.player._update_animation(dt)
            return

        if self._pickup_fx_timer > 0:
            self._pickup_fx_timer = max(0.0, self._pickup_fx_timer - dt)

        for coin in self.coins:
            coin.update(dt)

        if self.player.attack_pending:
            self._play_sfx("attack")

        collected_artifact = collision.collect_artifacts(self.player, self.artifacts, self.active_objects)
        if collected_artifact is not None:
            self._apply_artifact_effect(collected_artifact)
            self.score += 50
            self._play_sfx("artifact")

        collected_coin = collision.collect_coins(self.player, self.coins, self.active_objects)
        if collected_coin is not None:
            self.score += 10
            self._play_sfx("coin")

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
            if not enemy.is_alive and id(enemy) not in self._rewarded_enemy_ids:
                self._rewarded_enemy_ids.add(id(enemy))
                self.score += 100
                self._play_sfx("enemy_down")

        if self.player.lives < self._last_player_lives:
            self._play_sfx("hurt")
        self._last_player_lives = self.player.lives

        if self.player.pos.x < 0:
            self.player.pos.x = 0
        else:
            world_right = self._get_world_right_bound()
            if self.player.pos.x > world_right - P_WIDTH:
                self.player.pos.x = world_right - P_WIDTH

        if not self.player.is_alive:
            self.game_over = True

        if self.player.pos.y > self.death_y:
            if self.player.take_damage(1, ignore_invuln=True):
                if not self.player.is_alive:
                    self.game_over = True
                else:
                    self.player.respawn(self.player_spawn)

        if self._is_victory():
            self.game_won = True
            if not self._victory_sound_played:
                self._play_sfx("victory")
                self._victory_sound_played = True

        self._update_camera()   

    def draw(self, surface):
        cam = int(self.camera_x)
        for plat in self.platforms:
            plat.draw(surface, cam)
        
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

        finish_x = int(self.world_end_x - cam)
        if -10 <= finish_x <= SCREEN_W + 10:
            pygame.draw.line(surface, (255, 250, 90), (finish_x, 0), (finish_x, SCREEN_H), 3)
            pygame.draw.polygon(
                surface,
                (255, 80, 80),
                [(finish_x + 3, 20), (finish_x + 40, 32), (finish_x + 3, 44)],
            )

        if self._pickup_fx_timer > 0 and self.player.is_alive:
            center_x = int(self.player.rect.centerx - cam)
            center_y = int(self.player.rect.centery)
            radius = int(18 + (1.0 - self._pickup_fx_timer / 0.45) * 14)
            pygame.draw.circle(surface, self._pickup_fx_color, (center_x, center_y), radius, 3)

        for i, artifact in enumerate(self.player.artifacts):
            artifact.pos.x = 12 + i * 28
            artifact.pos.y = 80
            artifact.draw(surface, 0)
        
    def get_artifact_info(self):
        return f"Artifacts: {len(self.player.artifacts)}/3"

    def get_score_text(self):
        return f"Score: {self.score}"

    def generate_random_positions(self):
        x = random.randint(P_WIDTH, WORLD_WIDTH - P_WIDTH)
        y = random.randint(SCREEN_H - GROUND_Y , 360)
        return x, y
