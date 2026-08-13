from pathlib import Path
import pygame
from pygame.locals import *

from src.entities.animation import Animation
from src.entities.character import Character
from src.entities.sprite_manager import SpriteManager
from src.utils.config import (
    DRAW_HEIGHT,
    DRAW_WIDTH,
    JUMP_SPEED,
    P_HEIGHT,
    P_WIDTH,
    PLAYER_SPEED,
    RED,
)


class Player(Character):
    _frames_cache: dict[str, list[pygame.Surface]] | None = None

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
        self.is_attacking = False

        self._load_animations()
        self.set_animation("idle")

    def _load_animations(self):
        if Player._frames_cache is None:
            root = Path(__file__).resolve().parents[2]
            d = root / "assets" / "sprites" / "with_outline"
            Player._frames_cache = {
                "idle":   SpriteManager.load_strip(d / "IDLE.png",     96),
                "run":    SpriteManager.load_strip(d / "RUN.png",      96),
                "jump":   SpriteManager.load_strip(d / "JUMP.png",     96),
                "attack": SpriteManager.load_strip(d / "ATTACK 1.png", 96),
                "hurt":   SpriteManager.load_strip(d / "HURT.png",     96),
                "death":  SpriteManager.load_strip(d / "DEATH.png",    96),
            }

        f = Player._frames_cache
        self.animations = {
            "idle":   Animation.from_surfaces(f["idle"],   fps=8,  draw_width=DRAW_WIDTH, draw_height=DRAW_HEIGHT, loop=True),
            "run":    Animation.from_surfaces(f["run"],    fps=12, draw_width=DRAW_WIDTH, draw_height=DRAW_HEIGHT, loop=True),
            "jump":   Animation.from_surfaces(f["jump"],   fps=10, draw_width=DRAW_WIDTH, draw_height=DRAW_HEIGHT, loop=False),
            "attack": Animation.from_surfaces(f["attack"], fps=16, draw_width=DRAW_WIDTH, draw_height=DRAW_HEIGHT, loop=False),
            "hurt":   Animation.from_surfaces(f["hurt"],   fps=10, draw_width=DRAW_WIDTH, draw_height=DRAW_HEIGHT, loop=False),
            "death":  Animation.from_surfaces(f["death"],  fps=8,  draw_width=DRAW_WIDTH, draw_height=DRAW_HEIGHT, loop=False),
        }
        self._set_first_animation()

    def handle_input(self):
        if not self.is_alive:
            self.vel.x = 0
            self.move_input = False
            return

        keys = pygame.key.get_pressed()
        left_pressed  = keys[K_LEFT] or keys[K_a]
        right_pressed = keys[K_RIGHT] or keys[K_d]
        self.move_input = left_pressed or right_pressed

        self.vel.x = 0
        if left_pressed and not right_pressed:
            self.vel.x = -PLAYER_SPEED
            self.facing_right = False
        elif right_pressed and not left_pressed:
            self.vel.x = PLAYER_SPEED
            self.facing_right = True

        if (keys[K_RCTRL] or keys[K_LCTRL]) and self.move_input:
            self.vel.x *= 1.5

        if (keys[K_UP] or keys[K_w] or keys[K_SPACE]) and self.on_ground:
            self.vel.y = JUMP_SPEED
            self.on_ground = False

        if keys[K_k] and self.attack_cooldown == 0.0 and not self.is_attacking:
            self._start_attack()

    def _start_attack(self):
        super()._start_attack()
        self.is_attacking = True
        self.set_animation("attack")

    def _logic_state_machine(self):
        if not self.animations:
            return

        if not self.is_alive:
            self.set_animation("death")
            return

        if self.hurt_timer > 0:
            self.set_animation("hurt")
            return

        if self.is_attacking:
            current_anim = self.current_animation
            if (current_anim and current_anim.is_finished) or self.attack_timer == 0:
                self.is_attacking = False
            else:
                self.set_animation("attack")
                return

        if not self.on_ground:
            self.set_animation("jump")
            return

        if self.move_input and abs(self.vel.x) > 0:
            self.set_animation("run")
        else:
            self.set_animation("idle")

    def update(self, dt):
        self.handle_input()
        self.update_common(dt)
        self._logic_state_machine()
        self._update_animation(dt)

    def update_common(self, dt):
        super().update_common(dt)
        if self.hurt_timer > 0:
            self.hurt_timer = max(0.0, self.hurt_timer - dt)

    def take_damage(self, amount=1, ignore_invuln=False):
        damaged = super().take_damage(amount, ignore_invuln=ignore_invuln)
        if damaged and self.is_alive:
            if self.lives == 0:
                self.is_alive = False
                self.active = False
                self.vel.x = 0
                self.vel.y = 0
            else:
                self.hurt_timer = self.hurt_duration
                self.is_attacking = False
        return damaged

    def respawn(self, spawn_pos):
        self.pos.x = spawn_pos.x
        self.pos.y = spawn_pos.y
        self.vel.x = 0
        self.vel.y = 0
        self.on_ground = False
        self.is_alive = True
        self.active = True
        self.is_attacking = False
        self.set_animation("idle")