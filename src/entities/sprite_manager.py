import pygame
from pathlib import Path


class SpriteManager:
    _sheet_cache: dict[str, pygame.Surface] = {}

    @classmethod
    def _get_sheet(cls, filepath: str | Path) -> pygame.Surface | None:
        key = str(filepath)
        if key not in cls._sheet_cache:
            try:
                cls._sheet_cache[key] = pygame.image.load(key).convert_alpha()
            except pygame.error as e:
                print(f"[SpriteManager] Erro ao carregar '{key}': {e}")
                return None
        return cls._sheet_cache[key]

    @classmethod
    def load_strip(
        cls,
        filepath: str | Path,
        frame_width: int,
        frame_height: int | None = None,
    ) -> list[pygame.Surface]:
        sheet = cls._get_sheet(filepath)
        if sheet is None:
            return []

        fh = frame_height or sheet.get_height()
        cols = sheet.get_width() // frame_width
        rows = sheet.get_height() // fh

        return [
            sheet.subsurface(pygame.Rect(c * frame_width, r * fh, frame_width, fh)).copy()
            for r in range(rows)
            for c in range(cols)
        ]

    @classmethod
    def load_grid(
        cls,
        filepath: str | Path,
        frame_width: int,
        frame_height: int,
    ) -> list[pygame.Surface]:
        return cls.load_strip(filepath, frame_width, frame_height)