# entities/dynamic_object.py
from abc import abstractmethod

import pygame
from .game_object import GameObject
from src.utils.config import WHITE
from src.world import collision


class DynamicObject(GameObject):

    def __init__(self, pos, width: int, height: int, color= WHITE):
        super().__init__(pos, width, height, color)
        self.vel       = pygame.Vector2(0, 0)
        self.on_ground = False


    @abstractmethod
    def update(self, dt, world):
        pass

    def _apply_physics(self, dt: float, solids: list) -> None:
        collision.apply_gravity(self, dt)
        collision.move_with_platforms(self, solids, dt)