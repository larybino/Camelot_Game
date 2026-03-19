import pygame
from pygame.locals import *
from src.utils.config import (PLAYER_SPEED, GRAVITY, JUMP_SPEED, WHITE, RED, P_WIDTH, P_HEIGHT)


class Player:
    def __init__(self, x, y):
        self.pos       = pygame.Vector2(x, y)
        self.vel       = pygame.Vector2(0, 0)
        self.on_ground = False
    @property
    def rect(self):
        return pygame.Rect(int(self.pos.x), int(self.pos.y),
                           P_WIDTH, P_HEIGHT)
 
    def handle_input(self):
        keys = pygame.key.get_pressed()
 
        self.vel.x = 0
        if keys[K_LEFT] or keys[K_a]:
            if keys[K_RCTRL] or keys[K_LCTRL]:
                self.vel.x = -PLAYER_SPEED * 2
            else:
                self.vel.x = -PLAYER_SPEED
        if keys[K_RIGHT] or keys[K_d]:
            if keys[K_RCTRL] or keys[K_LCTRL]:
                self.vel.x = PLAYER_SPEED * 2
            else:
                self.vel.x = PLAYER_SPEED
        if (keys[K_UP] or keys[K_w] or keys[K_SPACE]) and self.on_ground:
            self.vel.y = JUMP_SPEED
            self.on_ground = False
 
    def update(self, dt, platforms):
        self.vel.y += GRAVITY * dt
 
        prev_pos = self.pos.copy()
 
        self.pos.x += self.vel.x * dt
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel.x > 0:                          
                    self.pos.x = plat.rect.left - P_WIDTH
                elif self.vel.x < 0:                        
                    self.pos.x = plat.rect.right
                self.vel.x = 0
 
        self.on_ground = False
        self.pos.y += self.vel.y * dt
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel.y > 0:                         
                    self.pos.y = plat.rect.top - P_HEIGHT
                    self.vel.y = 0
                    self.on_ground = True
                elif self.vel.y < 0:                       
                    self.pos.y = plat.rect.bottom
                    self.vel.y = 0
 
    def draw(self, surface, camera_x):
        draw_x = int(self.pos.x) - camera_x
        draw_y = int(self.pos.y)
        pygame.draw.ellipse(surface, RED,
                            (draw_x, draw_y, P_WIDTH, P_HEIGHT))
        pygame.draw.ellipse(surface, WHITE,
                            (draw_x, draw_y, P_WIDTH, P_HEIGHT), 2)