import pygame
from src.utils.config import BROWN, GREEN, GREY
from src.world.game_object import GameObject

class Platform(GameObject):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, BROWN if height >= 40 else GREY)
        self.grass_color = GREEN

    def draw(self, surface, parallax_factor=0):
        draw_rect = self.rect.move(-parallax_factor, 0)
        pygame.draw.rect(surface, self.color, draw_rect)
        grass_rect = pygame.Rect(draw_rect.x, draw_rect.y - 10, draw_rect.width, 10)
        pygame.draw.rect(surface, self.grass_color, grass_rect)