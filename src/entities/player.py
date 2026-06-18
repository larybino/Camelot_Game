import pygame
from pathlib import Path
from pygame.locals import *
from src.entities.animation import Animation
from src.entities.sprite_manager import SpriteManager
from src.entities.sprite import Sprite
from src.utils.config import (
    DRAW_HEIGHT,
    DRAW_WIDTH,
    PLAYER_SPEED,
    JUMP_SPEED,
    RED,
    P_WIDTH,
    P_HEIGHT,
)
from src.entities.character import Character


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

        self._load_animations()
        if self.sprite:
            self.sprite.set_animation("idle")

   
    def _load_animations(self):
        if Player._frames_cache is None:
            root = Path(__file__).resolve().parents[2]
            d = root / "assets" / "sprites" / "with_outline"
            Player._frames_cache = {
                "idle":   SpriteManager.load_strip(d / "IDLE.png",     84),
                "run":    SpriteManager.load_strip(d / "RUN.png",      96),
                "jump":   SpriteManager.load_strip(d / "JUMP.png",     96),
                "attack": SpriteManager.load_strip(d / "ATTACK 1.png", 96),
                "hurt":   SpriteManager.load_strip(d / "HURT.png",     96),
                "death":  SpriteManager.load_strip(d / "DEATH.png",    96),
            }
 
        f = Player._frames_cache
        self.sprite = Sprite(
            animations={
                "idle":   Animation(f["idle"],   fps=8),
                "run":    Animation(f["run"],    fps=12),
                "jump":   Animation(f["jump"],   fps=10, loop=False),
                "attack": Animation(f["attack"], fps=12, loop=False),
                "hurt":   Animation(f["hurt"],   fps=10, loop=False),
                "death":  Animation(f["death"],  fps=8,  loop=False),
            },
            draw_width=DRAW_WIDTH,
            draw_height=DRAW_HEIGHT,
        )
 
 
    def _logic_state_machine(self):
        if not self.sprite:
            return
 
        if self.is_dead:
            self.sprite.set_animation("death")
        elif self.hurt_timer > 0:
            self.sprite.set_animation("hurt")
        elif self.attack_timer > 0:
            self.sprite.set_animation("attack")
        elif not self.on_ground:
            self.sprite.set_animation("jump")
        elif self.move_input and abs(self.vel.x) > 1:
            self.sprite.set_animation("run")
        else:
            current = self.sprite.current_animation
            if current is None or current.is_finished or \
               self.sprite._current_key not in ("attack", "hurt", "death"):
                self.sprite.set_animation("idle")
    
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
        self._logic_state_machine()
        self._update_animation(dt)

        if abs(self.vel.x) > 1:
            self.facing_right = self.vel.x > 0

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
                self.vel.x = 0
                self.vel.y = 0
            else:
                self.hurt_timer = self.hurt_duration
        return damaged

   
    def respawn(self, spawn_pos):
        self.pos.x = spawn_pos.x
        self.pos.y = spawn_pos.y
        self.vel.x = 0
        self.vel.y = 0
        self.on_ground = False
        self.is_dead = False
        self.active = True
        if self.sprite:
            self.sprite.set_animation("idle")