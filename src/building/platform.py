from src.utils.config import BROWN, GREEN, GREY
from src.world.static_object import StaticObject

class Platform(StaticObject):
    def __init__(self, x, y, width, height):
        color = BROWN if height >= 40 else GREY
        super().__init__(x, y, width, height, color, grass_color=GREEN)