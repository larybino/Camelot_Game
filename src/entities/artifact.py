import random

import pygame
from pygame.locals import *
from src.utils.config import (A_HEIGHT, A_WIDTH, CYAN, GOLD, P_WIDTH, SCREEN_H, WORLD_WIDTH, GROUND_Y)
from src.world.game_object import GameObject

class Artifact(GameObject):
    def __init__(self, name, power, x = None, y = None):
        super().__init__(
            x or random.randint(P_WIDTH, WORLD_WIDTH - P_WIDTH), 
            y or random.randint(SCREEN_H - GROUND_Y , 360),
            A_WIDTH, A_HEIGHT, CYAN)
        
        self.name      = name
        self.power     = power

    @property
    def rect(self):
        return pygame.Rect(int(self.pos.x), int(self.pos.y),
                           self.width, self.height)
 
    def update(self, platforms):
        plat_id = self.rect.collidelist(platforms)
        if plat_id != -1:
            self.pos.x = platforms[plat_id].rect.centerx - self.width
            self.pos.y = platforms[plat_id].rect.top - self.height 
 
    def draw(self, surface, parallax_factor=0, platforms=[]):
        self.update(platforms)
        draw_rect = self.rect.move(-parallax_factor, 0)
        pygame.draw.ellipse(surface, CYAN,
                            (draw_rect.x, int(self.pos.y), self.width, self.height))
        pygame.draw.ellipse(surface, GOLD,
                            (draw_rect.x, int(self.pos.y), self.width, self.height), 2)