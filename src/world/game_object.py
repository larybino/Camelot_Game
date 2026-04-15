import pygame
from abc import ABC, abstractmethod
from src.utils.config import WHITE

class GameObject(ABC):
    def __init__(self, x, y, width, height, color=WHITE):
        self.pos = pygame.Vector2(x, y)
        self.width = width
        self.height = height
        self.color = color
        self.active = True

    @property
    def rect(self):
        return pygame.Rect(int(self.pos.x), int(self.pos.y), self.width, self.height)

    def handle_event(self, event, world):
        pass

    @abstractmethod
    def draw(self, surface, camera_x):
        pass
