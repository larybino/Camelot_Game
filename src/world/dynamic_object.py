# entities/dynamic_object.py
from abc import abstractmethod

import pygame
from .game_object import GameObject
from src.utils.config import GRAVITY, WHITE


class DynamicObject(GameObject):

    def __init__(self, x: float, y: float, width: int, height: int, color= WHITE):
        super().__init__(x, y, width, height, color)
        self.vel       = pygame.Vector2(0, 0)
        self.on_ground = False


    @abstractmethod
    def update(self, dt, world):
        pass

    # @abstractmethod
    # def update(self, dt: float, solids: list) -> None:
        # pass

    def _apply_physics(self, dt: float, solids: list) -> None:
        self.vel.y += GRAVITY * dt

        self.pos.x += self.vel.x * dt
        for obj in solids:
            if self.rect.colliderect(obj.rect):
                if self.vel.x > 0:
                    self.pos.x = obj.rect.left - self.width
                elif self.vel.x < 0:
                    self.pos.x = obj.rect.right
                self.vel.x = 0

        self.on_ground = False
        self.pos.y += self.vel.y * dt
        for obj in solids:
            if self.rect.colliderect(obj.rect):
                if self.vel.y > 0:
                    self.pos.y = obj.rect.top - self.height
                    self.on_ground = True
                elif self.vel.y < 0:
                    self.pos.y = obj.rect.bottom
                self.vel.y = 0