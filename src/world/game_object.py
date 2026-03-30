import pygame
from pygame.locals import *
from src.utils.config import  WHITE
from abc import ABC, abstractmethod

class GameObject(ABC):
    def __init__(self, x, y, width, height, color=WHITE):
        self.pos          = pygame.Vector2(x, y)
        self._rect        = pygame.Rect(int(x), int(y), width, height)
        self.width        = width
        self.height       = height
        self.color        = color

    @property
    def rect(self):
        return self._rect
 
    @abstractmethod
    def draw(self, surface, off_camera_x):
        pass
