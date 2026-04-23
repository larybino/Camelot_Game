import pygame
from pathlib import Path
from pygame.locals import *
from src.utils.config import (PLAYER_SPEED, JUMP_SPEED, WHITE, RED, P_WIDTH, P_HEIGHT, WORLD_WIDTH, GRAVITY, DRAW_WIDTH, DRAW_HEIGHT, DRAW_Y_OFFSET, FOOT_ALIGN_BONUS)
from src.world.dynamic_object import DynamicObject


class Player(DynamicObject):
    ANIM_FPS = {
        "idle": 8,
        "run": 12,
        "jump": 10,
    }
    _assets_loaded = False
    _frames = {
        "idle": [],
        "run": [],
        "jump": [],
    }

    def __init__(self, x, y):
        super().__init__(x, y, P_WIDTH, P_HEIGHT, RED)
        self.on_ground = True
        self.alive     = True
        self.artifacts  = []
        self.move_input = False
        self.facing_right = True
        self.anim_state = "idle"
        self.anim_time = 0.0
        self.anim_index = 0
        self.current_frame = None

        self._load_assets()
        self._update_animation(0.0)

    @classmethod
    def _load_assets(cls):
        if cls._assets_loaded:
            return

        project_root = Path(__file__).resolve().parents[2]
        sprite_dir = project_root / "assets" / "sprites" / "with_outline"

        sprite_map = {
            "idle": ("IDLE.png", 84),
            "run": ("RUN.png", 96),
            "jump": ("JUMP.png", 96),
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
                frames = []
                for i in range(frame_count):
                    frame = sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height)).copy()
                    frames.append(frame)
                cls._frames[state] = frames
            except pygame.error:
                cls._frames[state] = []

        cls._assets_loaded = True

    def _update_animation(self, dt):
        if abs(self.vel.x) > 1:
            self.facing_right = self.vel.x > 0

        prev_state = self.anim_state
        if not self.on_ground:
            self.anim_state = "jump"
        elif self.move_input and abs(self.vel.x) > 1:
            self.anim_state = "run"
        else:
            self.anim_state = "idle"

        frames = self._frames.get(self.anim_state, [])
        if not frames:
            self.current_frame = None
            return

        if self.anim_state == "idle":
            self.anim_time = 0.0
            self.anim_index = 0
            self.current_frame = frames[0]
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
        keys = pygame.key.get_pressed()
        left_pressed = keys[K_LEFT] or keys[K_a]
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
        if(keys[K_RCTRL] or keys[K_LCTRL]):
            self.vel.x *= 2
 
    def update(self, dt, platforms):
        self.handle_input()

        self.vel.y += GRAVITY * dt
 
        self.pos.x += self.vel.x * dt
        plat_id = self.rect.collidelist(platforms)
        if plat_id != -1:
            if self.vel.x > 0:                          
                self.pos.x = platforms[plat_id].rect.left - self.width
            elif self.vel.x < 0:                        
                self.pos.x = platforms[plat_id].rect.right
            self.vel.x = 0
 
        self.pos.y += self.vel.y * dt
        plat_id = self.rect.collidelist(platforms)
        if plat_id != -1:
            if self.vel.y > 0:                         
                self.pos.y = platforms[plat_id].rect.top - self.height
                self.on_ground = True
            elif self.vel.y < 0:                       
                self.pos.y = platforms[plat_id].rect.bottom
            self.vel.y = 0

        self._update_animation(dt)

    def handle_ladders(self, dt, ladder):
        if self.rect.centerx > ladder.rect.centerx and self.rect.bottom - 14 > ladder.rect.top :
            self.pos.x = ladder.rect.left - P_WIDTH + 10

        self.vel.x = 0
        self.vel.y = 0
        self.on_ground = True
        self.move_input = False
        keys = pygame.key.get_pressed()
        climb_speed = PLAYER_SPEED * 0.5
        if keys[K_UP] or keys[K_w] or keys[K_SPACE] or keys[K_RIGHT] or keys[K_d]:
            self.pos.y -= climb_speed * dt
        elif keys[K_DOWN] or keys[K_s] or keys[K_LEFT] or keys[K_a]:
            self.pos.y += PLAYER_SPEED * dt // 2

        self._update_animation(dt)
 
    def draw(self, surface, camera_x):
        draw_x, draw_y = int(self.pos.x) - camera_x, int(self.pos.y)
        if self.current_frame is None:
            pygame.draw.ellipse(surface, self.color,
                                (draw_x, draw_y, self.width, self.height))
            pygame.draw.ellipse(surface, WHITE,
                                (draw_x, draw_y, self.width, self.height), 2)
            return

        frame = self.current_frame
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)

        bounds = frame.get_bounding_rect(min_alpha=1)
        bottom_padding = max(0, frame.get_height() - bounds.bottom)
        scale_y = DRAW_HEIGHT / frame.get_height()
        feet_correction = int(bottom_padding * scale_y)

        sprite = pygame.transform.scale(frame, (DRAW_WIDTH, DRAW_HEIGHT))
        sprite_x = draw_x + (self.width - DRAW_WIDTH) // 2
        sprite_y = draw_y + (self.height - DRAW_HEIGHT) + DRAW_Y_OFFSET + feet_correction + FOOT_ALIGN_BONUS
        surface.blit(sprite, (sprite_x, sprite_y))