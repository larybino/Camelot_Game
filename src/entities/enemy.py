import pygame
from pathlib import Path
from src.utils.config import (
    RED,
    P_WIDTH,
    P_HEIGHT,
)
from src.entities.character import Character
from src.world import collision
class Enemy(Character):

    ANIM_FPS = {}
    _assets_loaded = False
    _frames = {}
    DEATH_LINGER = 2.0

    def __init__(self, pos, attacks=None,
                 max_lives=1, attack_interval=0.8,
                 attack_range_x=60, attack_range_y=40):
        super().__init__(
            pos,
            P_WIDTH,
            P_HEIGHT,
            RED,
            max_lives=max_lives,
            invuln_duration=0.0,
            attack_interval=attack_interval,
            attack_range_x=attack_range_x,
            attack_range_y=attack_range_y,
        )
        self.attacks = attacks or []
        self.death_timer = 0.0


    def _apply_physics(self, dt, platforms):
        collision.apply_gravity(self, dt)
        collision.move_with_platforms(self, platforms, dt)


    def _update_animation(self, dt):
        if self.is_dead:
            new_state = "death"
        elif self.attack_timer > 0:
            new_state = "attack"
        else:
            new_state = "idle"

        if new_state != self.anim_state:
            self.anim_state = new_state
            self.anim_time = 0.0
            self.anim_index = 0

        frames = self._frames.get(self.anim_state, [])
        if not frames:
            self.current_frame = None
            return

        if self.anim_state == "death" and self.anim_index >= len(frames) - 1:
            self.current_frame = frames[-1]
            return

        self.anim_time += dt
        fps = self.ANIM_FPS.get(self.anim_state, 8)
        self.anim_index = int(self.anim_time * fps) % len(frames)
        self.current_frame = frames[self.anim_index]

   
    def update(self, dt, platforms, player=None):
        if self.is_dead:
            self.death_timer -= dt
            if self.death_timer <= 0.0:
                self.active = False
            else:
                self._update_animation(dt)
            return

        self.update_common(dt)
        self._on_update(dt, player)
        self._update_animation(dt)
        self._apply_physics(dt, platforms)

    def _on_update(self, dt, player):
        pass

   
    def _start_attack(self):
        frames = self._frames.get("attack", [])
        fps = self.ANIM_FPS.get("attack", 6)
        duration = len(frames) / fps if frames else 0.5
        self.attack_timer = duration
        self.attack_cooldown = self.attack_interval
        self.anim_state = "attack"
        self.anim_time = 0.0
        self.anim_index = 0

    def _deal_damage(self, target):
        if self.attacks:
            self.attacks[0](self, target)
        elif hasattr(target, "take_damage"):
            target.take_damage(1)

  
    def take_damage(self, amount=1, ignore_invuln=False):
        if super().take_damage(amount, ignore_invuln=True):
            if self.lives == 0:
                self.is_dead = True
                self.death_timer = self.DEATH_LINGER
                self.vel.x = 0
                self.vel.y = 0