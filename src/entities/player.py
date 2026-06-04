import pygame
from pathlib import Path
from pygame.locals import *
from src.utils.config import (
    PLAYER_SPEED,
    JUMP_SPEED,
    RED,
    P_WIDTH,
    P_HEIGHT,
)
from src.entities.character import Character


class Player(Character):
    ANIM_FPS = {
        "idle": 8,
        "run": 12,
        "jump": 10,
        "attack": 12,
        "hurt": 10,
        "death": 8,
    }
    _assets_loaded = False
    _frames = {
        "idle": [],
        "run": [],
        "jump": [],
        "attack": [],
        "hurt": [],
        "death": [],
    }

    def __init__(self, pos):
        super().__init__(
            pos,
            P_WIDTH,
            P_HEIGHT,
            RED,
            max_lives=3,
            invuln_duration=0.8,
            attack_interval=0.45,
            attack_range_x=50,
            attack_range_y=40,
        )
        self.on_ground = True
        self.artifacts = []
        self.hurt_timer = 0.0
        self.hurt_duration = 0.15

        self._load_assets()
        self._update_animation(0.0)

    @classmethod
    def _load_assets(cls):
        if cls._assets_loaded:
            return

        project_root = Path(__file__).resolve().parents[2]
        sprite_dir = project_root / "assets" / "sprites" / "with_outline"

        sprite_map = {
            "idle":   ("IDLE.png",     84),
            "run":    ("RUN.png",      96),
            "jump":   ("JUMP.png",     96),
            "attack": ("ATTACK 1.png", 96),
            "hurt":   ("HURT.png",     96),
            "death":  ("DEATH.png",    96),
        }

        for state, (file_name, frame_width) in sprite_map.items():
            file_path = sprite_dir / file_name
            if not file_path.exists():
                cls._frames[state] = []
                continue
            try:
                sheet = pygame.image.load(str(file_path)).convert_alpha()
                frame_height = sheet.get_height()
                frame_count = sheet.get_width() // frame_width
                cls._frames[state] = [
                    sheet.subsurface(
                        pygame.Rect(i * frame_width, 0, frame_width, frame_height)
                    ).copy()
                    for i in range(frame_count)
                ]
            except pygame.error:
                cls._frames[state] = []

        cls._assets_loaded = True

    def _update_animation(self, dt):
        if abs(self.vel.x) > 1:
            self.facing_right = self.vel.x > 0

        prev_state = self.anim_state

        if self.is_dead:
            self.anim_state = "death"
        elif self.hurt_timer > 0:
            self.anim_state = "hurt"
        elif self.attack_timer > 0:
            self.anim_state = "attack"
        elif not self.on_ground:
            self.anim_state = "jump"
        elif self.move_input and abs(self.vel.x) > 1:
            self.anim_state = "run"
        elif self.anim_state == "attack":
            death_frames = self._frames.get("attack", [])
            if death_frames and self.anim_index == len(death_frames) - 1:
                self.anim_state = "idle"
        else:
            self.anim_state = "idle"

        frames = self._frames.get(self.anim_state, [])
        if not frames:
            self.current_frame = None
            return

        if self.anim_state in ("idle", "jump"):
            self.anim_time = 0.0
            self.anim_index = 0
            self.current_frame = frames[0]
            return

        if self.anim_state == "death" and self.anim_index == len(frames) - 1:
            self.current_frame = frames[self.anim_index]
            return

        if self.anim_state != prev_state:
            self.anim_time = 0.0
            self.anim_index = 0
        else:
            self.anim_time += dt
            step = 1.0 / self.ANIM_FPS[self.anim_state]
            while self.anim_time >= step:
                self.anim_time -= step
                self.anim_index = (self.anim_index + 1) % len(frames)

        self.current_frame = frames[self.anim_index]

   
    def handle_input(self):
        if self.is_dead:
            self.vel.x = 0
            return

        keys = pygame.key.get_pressed()
        left_pressed  = keys[K_LEFT] or keys[K_a]
        right_pressed = keys[K_RIGHT] or keys[K_d]
        self.move_input = left_pressed or right_pressed

        self.vel.x = 0
        if left_pressed and not right_pressed:
            self.vel.x = -PLAYER_SPEED
        if right_pressed and not left_pressed:
            self.vel.x = PLAYER_SPEED
        if (keys[K_UP] or keys[K_w] or keys[K_SPACE]) and self.on_ground:
            self.vel.y = JUMP_SPEED
            self.on_ground = False
        if keys[K_RCTRL] or keys[K_LCTRL]:
            self.vel.x *= 2
        if keys[K_k] and self.attack_cooldown == 0.0:
            self._start_attack()

  
    def update(self, dt, platforms):
        self.handle_input()
        self.update_common(dt)
        self._update_animation(dt)

    def update_common(self, dt):
        super().update_common(dt)
        if self.hurt_timer > 0:
            self.hurt_timer = max(0.0, self.hurt_timer - dt)

  
    def take_damage(self, amount=1, ignore_invuln=False):
        damaged = super().take_damage(amount, ignore_invuln=ignore_invuln)
        if damaged and not self.is_dead:
            if self.lives == 0:
                self.is_dead = True
                self.active = False
                self.anim_state = "death"
                self.anim_time = 0.0
                self.anim_index = 0
                self.vel.x = 0
                self.vel.y = 0
            else:
                self.hurt_timer = self.hurt_duration
                self.anim_state = "hurt"
                self.anim_time = 0.0
                self.anim_index = 0
        return damaged

   
    def respawn(self, spawn_pos):
        self.pos.x = spawn_pos.x
        self.pos.y = spawn_pos.y
        self.vel.x = 0
        self.vel.y = 0
        self.on_ground = False
        self.is_dead = False
        self.active = True