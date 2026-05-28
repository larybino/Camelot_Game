from pathlib import Path

import pygame

from src.utils.config import BROWN, GREEN, GREY, TILE_SIZE
from src.world.static_object import StaticObject


class Platform(StaticObject):
    _top_tile = None
    _body_tile = None
    _load_attempted = False

    def __init__(self, pos, width, height):
        color = BROWN if height >= 40 else GREY
        super().__init__(pos, width, height, color, grass_color=GREEN)

    @classmethod
    def _load_tiles(cls):
        if cls._load_attempted:
            return

        cls._load_attempted = True
        project_root = Path(__file__).resolve().parents[2]
        sheet_path = project_root / "assets" / "sprites" / "brackeys_platformer_assets" / "sprites" / "world_tileset.png"

        if not sheet_path.exists():
            return

        try:
            sheet = pygame.image.load(str(sheet_path)).convert_alpha()
            cls._top_tile = sheet.subsurface(pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)).copy()
            cls._body_tile = sheet.subsurface(pygame.Rect(TILE_SIZE, 0, TILE_SIZE, TILE_SIZE)).copy()
        except pygame.error:
            cls._top_tile = None
            cls._body_tile = None

    @staticmethod
    def _blit_tile(surface, tile, x, y, w, h):
        if w <= 0 or h <= 0:
            return
        if w == tile.get_width() and h == tile.get_height():
            surface.blit(tile, (x, y))
            return
        surface.blit(pygame.transform.scale(tile, (w, h)), (x, y))

    def draw(self, surface, camera_x) -> None:
        self._load_tiles()
        if self._top_tile is None or self._body_tile is None:
            super().draw(surface, camera_x)
            return

        draw_rect = self.rect.move(-camera_x, 0)
        tile = TILE_SIZE

        for offset_x in range(0, draw_rect.width, tile):
            chunk_w = min(tile, draw_rect.width - offset_x)
            self._blit_tile(surface, self._top_tile, draw_rect.x + offset_x, draw_rect.y, chunk_w, min(tile, draw_rect.height))

            for offset_y in range(tile, draw_rect.height, tile):
                chunk_h = min(tile, draw_rect.height - offset_y)
                self._blit_tile(surface, self._body_tile, draw_rect.x + offset_x, draw_rect.y + offset_y, chunk_w, chunk_h)