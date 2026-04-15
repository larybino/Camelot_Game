from src.utils.config import BLUE
from src.world.static_object import StaticObject

class Lake(StaticObject):
    def __init__(self, x, y, width, height):
        color = BLUE
        super().__init__(x, y, width, height, color)