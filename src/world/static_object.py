import pygame
from .game_object import GameObject


class StaticObject(GameObject):

    def __init__(self, x, y, width, height, color, grass_color=None):
        super().__init__(x, y, width, height, color)
        self.grass_color = grass_color

    def draw(self, surface, camera_x) -> None:
        draw_rect  = self.rect.move(-camera_x, 0)
        pygame.draw.rect(surface, self.color, draw_rect)
        if self.grass_color:
            grass_rect = pygame.Rect(draw_rect.x, draw_rect.y,
                                     draw_rect.width, 10)
            pygame.draw.rect(surface, self.grass_color, grass_rect)
