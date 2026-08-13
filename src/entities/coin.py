from pathlib import Path

import pygame

from src.entities.animation import Animation
from src.entities.sprite_manager import SpriteManager
from src.utils.config import A_HEIGHT, A_WIDTH, DRAW_SIZE, GOLD
from src.world.game_object import GameObject


class Coin(GameObject):
    _frames_cache: list[pygame.Surface] | None = None

    def __init__(self, pos):
        super().__init__(pos, A_WIDTH, A_HEIGHT, GOLD)
        self.animation = self._build_animation()

    @classmethod
    def _build_animation(cls) -> Animation | None:
        if cls._frames_cache is None:
            root = Path(__file__).resolve().parents[2]
            path = (
                root / "assets" / "sprites" / "brackeys_platformer_assets" / "sprites" / "coin.png"
            )
            if path.exists():
                sheet = SpriteManager._get_sheet(path)
                if sheet is not None:
                    frame_size = sheet.get_height()
                    cls._frames_cache = SpriteManager.load_strip(path, frame_size)
                else:
                    cls._frames_cache = []
            else:
                cls._frames_cache = []

        if not cls._frames_cache:
            return None

        return Animation.from_surfaces(
            cls._frames_cache,
            fps=12,
            draw_width=DRAW_SIZE,
            draw_height=DRAW_SIZE,
            loop=True,
        )

    def update(self, dt):
        if self.animation:
            self.animation.update(dt)

    def draw(self, surface, camera_x=0):
        draw_rect = self.rect.move(-camera_x, 0)
        if self.animation:
            self.animation.draw(
                surface,
                draw_rect.x,
                draw_rect.y,
                char_width=self.width,
                char_height=self.height,
            )
            return

        pygame.draw.ellipse(surface, self.color, (draw_rect.x, draw_rect.y, self.width, self.height))