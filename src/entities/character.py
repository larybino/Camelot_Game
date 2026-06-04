import pygame
from src.world.dynamic_object import DynamicObject
from src.entities.health import Health
from src.utils.config import (
    WHITE,
    DRAW_WIDTH,
    DRAW_HEIGHT,
    DRAW_Y_OFFSET,
    FOOT_ALIGN_BONUS,
)


class Character(DynamicObject):
    ANIM_FPS = {}
    _assets_loaded = False
    _frames = {}

    def __init__(
        self,
        pos,
        width,
        height,
        color,
        max_lives=3,
        invuln_duration=0.8,
        attack_interval=0.45,
        attack_range_x=50,
        attack_range_y=40,
        draw_width=None,
        draw_height=None,
    ):
        super().__init__(pos, width, height, color)
        self.health = Health(max_lives=max_lives, invuln_duration=invuln_duration)
        self.facing_right = True
        self.anim_state = "idle"
        self.anim_time = 0.0
        self.anim_index = 0
        self.current_frame = None
        self.attack_cooldown = 0.0
        self.attack_interval = attack_interval
        self.attack_timer = 0.0
        self.attack_pending = False
        self.attack_range_x = attack_range_x
        self.attack_range_y = attack_range_y
        self.move_input = False
        self.is_dead = False
        self.active = True
        self.draw_width  = draw_width  or DRAW_WIDTH
        self.draw_height = draw_height or DRAW_HEIGHT

    
    @classmethod
    def _load_assets(cls):
        pass

   
    def _update_animation(self, dt):
        pass

   
    def update_common(self, dt):
        self.health.update(dt)
        self._update_attack(dt)

    def _update_attack(self, dt):
        if self.attack_cooldown > 0:
            self.attack_cooldown = max(0.0, self.attack_cooldown - dt)
        if self.attack_timer > 0:
            self.attack_timer = max(0.0, self.attack_timer - dt)

    def _start_attack(self):
        self.attack_pending = True
        self.attack_timer = 0.25
        self.attack_cooldown = self.attack_interval
        self.anim_state = "attack"
        self.anim_time = 0.0
        self.anim_index = 0

    @property
    def lives(self):
        return self.health.lives

    @lives.setter
    def lives(self, value):
        self.health.lives = max(0, min(self.health.max_lives, int(value)))

    @property
    def max_lives(self):
        return self.health.max_lives

    @max_lives.setter
    def max_lives(self, value):
        self.health.max_lives = int(value)
        if self.health.lives > self.health.max_lives:
            self.health.lives = self.health.max_lives

    def take_damage(self, amount=1, ignore_invuln=False):
        return self.health.take_damage(amount, ignore_invuln=ignore_invuln)

   
    def consume_attack(self):
        if self.attack_pending:
            self.attack_pending = False
            return True
        return False

    def get_attack_rect(self):
        if self.facing_right:
            x = self.rect.right
        else:
            x = self.rect.left - self.attack_range_x
        y = self.rect.centery - (self.attack_range_y // 2)
        return pygame.Rect(x, y, self.attack_range_x, self.attack_range_y)

    
    def draw(self, surface, camera_x=0):
        draw_x = int(self.pos.x) - camera_x
        draw_y = int(self.pos.y)

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
        scale_y = self.draw_height / frame.get_height()
        feet_correction = int(bottom_padding * scale_y)

        sprite = pygame.transform.scale(frame, (self.draw_width, self.draw_height))
        sprite_x = draw_x + (self.width - self.draw_width) // 2
        sprite_y = (draw_y + (self.height - self.draw_height)
                    + DRAW_Y_OFFSET + feet_correction + FOOT_ALIGN_BONUS)
        surface.blit(sprite, (sprite_x, sprite_y))