import pygame
from pathlib import Path
from src.utils.config import BROWN, TILE_SIZE
from src.world.game_object import GameObject


class Ladder(GameObject):
    _ladder_tile = None
    _load_attempted = False

    def __init__(self, pos, width, height):
        super().__init__(pos, width, height, BROWN)

    @classmethod
    def _load_tiles(cls):
        if cls._load_attempted:
            return

        cls._load_attempted = True

        project_root = Path(__file__).resolve().parents[2]
        sheet_path = (
            project_root
            / "assets"
            / "sprites"
            / "brackeys_platformer_assets"
            / "sprites"
            / "world_tileset.png"
        )

        if not sheet_path.exists():
            return

        try:
            sheet = pygame.image.load(str(sheet_path)).convert_alpha()

            # Sprite da escada no tileset.
            # Pela sua imagem, a escada fica em x=9, y=3 (tile de 16x16).
            raw_tile = sheet.subsurface(pygame.Rect(9 * 16, 3 * 16, 16, 16)).copy()

            # A sprite tem uma faixa transparente no topo.
            # Vamos cortar só o vazio vertical para evitar os “buracos” ao repetir.
            visible_rect = raw_tile.get_bounding_rect()

            if visible_rect.height > 0:
                cls._ladder_tile = raw_tile.subsurface(
                    pygame.Rect(
                        0,
                        visible_rect.top,
                        raw_tile.get_width(),
                        visible_rect.height,
                    )
                ).copy()
            else:
                cls._ladder_tile = raw_tile

        except pygame.error:
            cls._ladder_tile = None

    def draw(self, surface, camera_x=0):
        self._load_tiles()

        draw_x = self.rect.x - camera_x
        draw_y = self.rect.y

        if self._ladder_tile is None:
            pygame.draw.rect(
                surface,
                self.color,
                (draw_x, draw_y, self.rect.width, self.rect.height)
            )
            return

        # Cria uma superfície da altura total da escada
        ladder_surface = pygame.Surface(
            (self.rect.width, self.rect.height),
            pygame.SRCALPHA
        )

        tile = self._ladder_tile

        original_w = tile.get_width()
        original_h = tile.get_height()

        # Ajusta a largura para caber na largura da escada
        if original_w != self.rect.width:
            tile = pygame.transform.scale(
                tile,
                (self.rect.width, original_h)
            )

        tile_h = tile.get_height()

        current_y = 0

        while current_y < self.rect.height:

            remaining = self.rect.height - current_y

            if remaining >= tile_h:
                ladder_surface.blit(tile, (0, current_y))
            else:
                partial = tile.subsurface(
                    pygame.Rect(
                        0,
                        0,
                        tile.get_width(),
                        remaining
                    )
                )
                ladder_surface.blit(partial, (0, current_y))

            current_y += tile_h

        surface.blit(
            ladder_surface,
            (draw_x, draw_y)
        )