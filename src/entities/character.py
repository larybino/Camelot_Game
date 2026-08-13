import pygame
from src.entities.animation import Animation
from src.world.dynamic_object import DynamicObject
from src.entities.health import Health
from src.utils.config import (
    WHITE,
    DRAW_Y_OFFSET,
    FOOT_ALIGN_BONUS,
)


class Character(DynamicObject):

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
        attack_damage=1,
    ):
        super().__init__(pos, width, height, color)
        self.health = Health(max_lives=max_lives, invuln_duration=invuln_duration)
        self.facing_right = True
        self.attack_cooldown = 0.0
        self.attack_interval = attack_interval
        self.attack_timer = 0.0
        self.attack_pending = False
        self.attack_range_x = attack_range_x
        self.attack_range_y = attack_range_y
        self.attack_damage = max(1, int(attack_damage))
        self.move_input = False
        self.is_alive = True
        self.active = True

        self.animations: dict[str, Animation] = {}
        self._current_animation_key: str = ""

   
    def _update_animation(self, dt: float):
        anim = self.current_animation
        if anim:
            anim.update(dt)

    def set_animation(self, key: str) -> None:
        if key == self._current_animation_key or key not in self.animations:
            return
        self._current_animation_key = key
        self.animations[key].reset()

    @property
    def current_animation(self) -> Animation | None:
        return self.animations.get(self._current_animation_key)

    def _set_first_animation(self) -> None:
        first = next(iter(self.animations), None)
        if first:
            self._current_animation_key = first
 
    def _logic_state_machine(self):
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
        self.set_animation("attack")

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

    
    def draw(self, surface: pygame.Surface, camera_x: int = 0) -> None:
        x = int(self.pos.x) - camera_x
        y = int(self.pos.y)
 
        anim = self.current_animation
        if anim is None:
            pygame.draw.ellipse(surface, self.color, (x, y, self.width, self.height))
            pygame.draw.ellipse(surface, WHITE, (x, y, self.width, self.height), 2)
            return
 
        anim.draw(
            surface, x, y,
            flip_h=not self.facing_right,
            char_width=self.width,
            char_height=self.height,
            y_offset=DRAW_Y_OFFSET,
            foot_bonus=FOOT_ALIGN_BONUS,
        )