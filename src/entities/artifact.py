from pathlib import Path

import pygame
from src.utils.config import (A_HEIGHT, A_WIDTH, CYAN, GOLD, DRAW_SIZE)
from src.world.game_object import GameObject


class Artifact(GameObject):
    _sprite_cache = {}
    _sprite_map = {
        "Excalibur": "Item__07.png",
        "Santo Graal": "Item__71.png",
        "Cajado de Merlim": "Item__20.png",
    }

    def __init__(self, name, power, x, y):
        super().__init__(x, y, A_WIDTH, A_HEIGHT, CYAN)
        self.name      = name
        self.power     = power

    @classmethod
    def _get_sprite(cls, name):
        if name in cls._sprite_cache:
            return cls._sprite_cache[name]

        file_name = cls._sprite_map.get(name)
        if not file_name:
            cls._sprite_cache[name] = None
            return None

        project_root = Path(__file__).resolve().parents[2]
        sprite_path = project_root / "assets" / "sprites" / "16x16 RPG Item Pack" / file_name
        if not sprite_path.exists():
            cls._sprite_cache[name] = None
            return None

        try:
            sprite = pygame.image.load(str(sprite_path)).convert_alpha()
            cls._sprite_cache[name] = sprite
            return sprite
        except pygame.error:
            cls._sprite_cache[name] = None
            return None

    def update(self, dt, world):
        plat_id = self.rect.collidelist(world.platforms)
        if plat_id != -1:
            self.pos.x = world.platforms[plat_id].rect.centerx - self.width
            self.pos.y = world.platforms[plat_id].rect.top - self.height

    def draw(self, surface, camera_x=0):
        draw_rect = self.rect.move(-camera_x, 0)

        sprite = self._get_sprite(self.name)
        if sprite is not None:
            sprite_scaled = pygame.transform.scale(sprite, (DRAW_SIZE, DRAW_SIZE))
            sprite_x = draw_rect.x + (self.width - DRAW_SIZE) // 2
            sprite_y = draw_rect.y + (self.height - DRAW_SIZE)
            surface.blit(sprite_scaled, (sprite_x, sprite_y))
            return

        pygame.draw.ellipse(surface, CYAN,
                            (draw_rect.x, int(self.pos.y), self.width, self.height))
        pygame.draw.ellipse(surface, GOLD,
                            (draw_rect.x, int(self.pos.y), self.width, self.height), 2)