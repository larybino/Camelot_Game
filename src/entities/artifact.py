import random

import pygame
from src.utils.config import (A_HEIGHT, A_WIDTH, CYAN, GOLD, P_WIDTH, SCREEN_H, WORLD_WIDTH, GROUND_Y)
from src.world.game_object import GameObject

class Artifact(GameObject):
    def __init__(self, name, power, x, y):
        super().__init__(x, y, A_WIDTH, A_HEIGHT, CYAN)
        self.name      = name
        self.power     = power

    def update(self, dt, world):
        plat_id = self.rect.collidelist(world.platforms)
        if plat_id != -1:
            self.pos.x = world.platforms[plat_id].rect.centerx - self.width
            self.pos.y = world.platforms[plat_id].rect.top - self.height

    def draw(self, surface, camera_x=0):
        draw_rect = self.rect.move(-camera_x, 0)
        pygame.draw.ellipse(surface, CYAN,
                            (draw_rect.x, int(self.pos.y), self.width, self.height))
        pygame.draw.ellipse(surface, GOLD,
                            (draw_rect.x, int(self.pos.y), self.width, self.height), 2)