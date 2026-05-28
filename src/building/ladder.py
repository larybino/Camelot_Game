import pygame
from src.utils.config import BROWN
from src.world.game_object import GameObject

class Ladder(GameObject):
    def __init__(self, pos, width, height):
        super().__init__(pos, width, height, BROWN)

    def draw(self, surface, camera_x=0):
        draw_rect = self.rect.move(-camera_x, 0)

        rung_height = 2
        rung_spacing = 10
        rail_width = 4

        left_rail = pygame.Rect(draw_rect.left, draw_rect.top, rail_width, draw_rect.height)
        right_rail = pygame.Rect(draw_rect.right - rail_width, draw_rect.top, rail_width, draw_rect.height)
        pygame.draw.rect(surface, self.color, left_rail)
        pygame.draw.rect(surface, self.color, right_rail)

        for y in range(draw_rect.top + rung_spacing, draw_rect.bottom, rung_spacing + rung_height):
            rung_rect = pygame.Rect(draw_rect.left, y, draw_rect.width, rung_height)
            pygame.draw.rect(surface, self.color, rung_rect)