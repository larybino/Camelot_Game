import pygame
from pygame.locals import *
from src.utils.config import (PLAYER_SPEED, JUMP_SPEED, WHITE, RED, P_WIDTH, P_HEIGHT, WORLD_WIDTH, GRAVITY)
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
            self.vel.x = -PLAYER_SPEED
        if keys[K_RIGHT] or keys[K_d]:
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
                self.pos.x = platforms[plat_id].rect.left - P_WIDTH
            elif self.vel.x < 0:                        
                self.pos.x = platforms[plat_id].rect.right
            self.vel.x = 0
 
        self.pos.y += self.vel.y * dt
        plat_id = self.rect.collidelist(platforms)
        if plat_id != -1:
            if self.vel.y > 0:                         
                self.pos.y = platforms[plat_id].rect.top - P_HEIGHT
                self.on_ground = True
            elif self.vel.y < 0:                       
                self.pos.y = platforms[plat_id].rect.bottom
            self.vel.y = 0

    def handle_ladders(self, dt, ladder):
        if self.rect.centerx > ladder.rect.centerx and self.rect.bottom - 14 > ladder.rect.top :
            self.pos.x = ladder.rect.left - P_WIDTH + 10

        self.vel.y = 0
        self.on_ground = True
        keys = pygame.key.get_pressed()
        climb_speed = PLAYER_SPEED * 0.5
        if keys[K_UP] or keys[K_w] or keys[K_SPACE] or keys[K_RIGHT] or keys[K_d]:
            self.pos.y -= climb_speed * dt
        elif keys[K_DOWN] or keys[K_s] or keys[K_LEFT] or keys[K_a]:
            self.pos.y += PLAYER_SPEED * dt // 2
 
    def draw(self, surface, camera_x):
        draw_x, draw_y = int(self.pos.x) - camera_x, int(self.pos.y)
        pygame.draw.ellipse(surface, self.color,
                            (draw_x, draw_y, self.width, self.height))
        pygame.draw.ellipse(surface, WHITE,
                            (draw_x, draw_y, self.width, self.height), 2)