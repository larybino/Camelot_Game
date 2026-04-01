# entities/static_object.py
import pygame
from .game_object import GameObject
from src.utils.config import GREEN


class StaticObject(GameObject):

    def __init__(self, x, y, width, height, color, grass_color=GREEN):
        super().__init__(x, y, width, height, color)
        self.grass_color = grass_color

    def update(self, dt, world) -> None:
        pass 

    def draw(self, surface, camera_x) -> None:
        draw_rect  = self.rect.move(-camera_x, 0)
        pygame.draw.rect(surface, self.color, draw_rect)
        grass_rect = pygame.Rect(draw_rect.x, draw_rect.y - 10,
                                 draw_rect.width, 10)
        pygame.draw.rect(surface, self.grass_color, grass_rect)
