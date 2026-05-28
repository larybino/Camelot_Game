import pygame
from src.utils.config import BLUE
from src.world.static_object import StaticObject

class Lake(StaticObject):
    def __init__(self, pos, width, height):
        color = BLUE
        super().__init__(pos, width, height, color)