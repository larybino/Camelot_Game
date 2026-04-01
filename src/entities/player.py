import pygame
from pygame.locals import *
from src.utils.config import (PLAYER_SPEED, JUMP_SPEED, WHITE, RED, P_WIDTH, P_HEIGHT, WORLD_WIDTH)
from src.world.dynamic_object import DynamicObject


class Player(DynamicObject):
    def __init__(self, x, y):
        super().__init__(x, y, P_WIDTH, P_HEIGHT, RED)
        self.on_ground = True
        self.alive     = True
        self.artifacts  = []

    def handle_input(self):
        keys = pygame.key.get_pressed()

        self.vel.x = 0
        if keys[K_LEFT] or keys[K_a]:
            self.vel.x = -PLAYER_SPEED * 2 if keys[K_RCTRL] or keys[K_LCTRL] else -PLAYER_SPEED
        if keys[K_RIGHT] or keys[K_d]:
            self.vel.x = PLAYER_SPEED * 2 if keys[K_RCTRL] or keys[K_LCTRL] else PLAYER_SPEED
        if (keys[K_UP] or keys[K_w] or keys[K_SPACE]) and self.on_ground:
            self.vel.y = JUMP_SPEED
            self.on_ground = False

    def update(self, dt, world):
        self.handle_input()

        if self.rect.collidelist(world.ladders) != -1:
            self.handle_ladders(dt)
        else:
            self._apply_physics(dt, world.platforms)

        if self.pos.x < 0:
            self.pos.x = 0
        elif self.pos.x > WORLD_WIDTH - self.width:
            self.pos.x = WORLD_WIDTH - self.width

        if self.pos.y > world.death_y:
            self.pos.update(world.player_spawn)
            self.vel.update(0, 0)

    def handle_ladders(self, dt):
        self.vel.y = 0
        self.on_ground = True
        keys = pygame.key.get_pressed()
        climb_speed = PLAYER_SPEED * 0.5
        if keys[K_UP] or keys[K_w] or keys[K_SPACE] or keys[K_RIGHT] or keys[K_d]:
            self.pos.y -= climb_speed * dt
        elif keys[K_DOWN] or keys[K_s] or keys[K_LEFT] or keys[K_a]:
            self.pos.y += climb_speed * dt

    def draw(self, surface, camera_x):
        draw_x, draw_y = int(self.pos.x) - camera_x, int(self.pos.y)
        pygame.draw.ellipse(surface, self.color,
                            (draw_x, draw_y, self.width, self.height))
        pygame.draw.ellipse(surface, WHITE,
                            (draw_x, draw_y, self.width, self.height), 2)