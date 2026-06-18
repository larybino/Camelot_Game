import pygame
from pathlib import Path

from src.utils.config import BLUE, BROWN, TILE_SIZE
from src.world.static_object import StaticObject

class Lake(StaticObject):
    _body_tile = None
    _water_top_tile = None
    _water_body_tile = None
    _load_attempted = False

    def __init__(self, pos, width, height):
        color = BLUE
        super().__init__(pos, width, height, color)

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
            
            cls._water_top_tile = sheet.subsurface(pygame.Rect(4 * TILE_SIZE, 9 * TILE_SIZE, TILE_SIZE, TILE_SIZE)).copy()
            
            cls._water_body_tile = sheet.subsurface(pygame.Rect(4 * TILE_SIZE, 10 * TILE_SIZE, TILE_SIZE, TILE_SIZE)).copy()
            cls._body_tile = sheet.subsurface(pygame.Rect(TILE_SIZE, 0, TILE_SIZE, TILE_SIZE)).copy()
        except pygame.error:
            cls._body_tile = None
            cls._water_top_tile = None
            cls._water_body_tile = None

    @staticmethod
    def _blit_tile(surface, tile, x, y, w, h):
        if w <= 0 or h <= 0:
            return
        if w == tile.get_width() and h == tile.get_height():
            surface.blit(tile, (x, y))
            return
        surface.blit(pygame.transform.scale(tile, (w, h)), (x, y))

    def _fill_rect_with_tiles(self, surface, rect):
        if self._body_tile is None:
            pygame.draw.rect(surface, BROWN, rect)
            return

        for offset_x in range(0, rect.width, TILE_SIZE):
            chunk_w = min(TILE_SIZE, rect.width - offset_x)
            for offset_y in range(0, rect.height, TILE_SIZE):
                chunk_h = min(TILE_SIZE, rect.height - offset_y)
                self._blit_tile(surface, self._body_tile, rect.x + offset_x, rect.y + offset_y, chunk_w, chunk_h)

    def _fill_rect_with_water_tiles(self, surface, rect):
        if self._water_top_tile is None or self._water_body_tile is None:
            pygame.draw.rect(surface, self.color, rect)
            return

        for offset_x in range(0, rect.width, TILE_SIZE):
            chunk_w = min(TILE_SIZE, rect.width - offset_x)
            for offset_y in range(0, rect.height, TILE_SIZE):
                chunk_h = min(TILE_SIZE, rect.height - offset_y)
                
                tile = self._water_top_tile if offset_y == 0 else self._water_body_tile
                
                self._blit_tile(surface, tile, rect.x + offset_x, rect.y + offset_y, chunk_w, chunk_h)

    def _get_geometry(self, rect):
        step_height = max(6, rect.height // 6)
        max_side_inset = max(8, rect.width // 5)
        max_side_inset = min(max_side_inset, rect.width // 2 - 2)

        steps = max(2, rect.height // step_height)
        inset_per_step = max(3, max_side_inset // max(1, steps - 1))
        total_inset = steps * inset_per_step

        if total_inset * 2 >= rect.width:
            total_inset = max(2, rect.width // 4)
            inset_per_step = max(1, total_inset // steps)

        left_inner = rect.left + total_inset
        right_inner = rect.right - total_inset

        if left_inner >= right_inner:
            middle = rect.centerx
            left_inner = middle - 1
            right_inner = middle + 1

        return {
            "left": rect.left,
            "right": rect.right,
            "top_y": rect.top,
            "bottom_y": rect.bottom,
            "step_height": step_height,
            "steps": steps,
            "inset_per_step": inset_per_step,
            "left_inner": left_inner,
            "right_inner": right_inner,
        }
    
    def get_step_height(self):
        geo = self._get_geometry(self.rect)
        return geo["step_height"]
 
    def in_lake_zone(self, rect, v_margin=None):
        if v_margin is None:
            v_margin = self.get_step_height()
 
        x_overlap = rect.right > self.rect.left and rect.left < self.rect.right
        if not x_overlap:
            return False
 
        y_overlap = rect.bottom > self.rect.top - v_margin
        return y_overlap

    def is_in_stair_zone(self, world_x):
        geo = self._get_geometry(self.rect)
        x = int(world_x)
        if x < geo["left"] or x >= geo["right"]:
            return False
        return x < geo["left_inner"] or x >= geo["right_inner"]

    def get_stair_surface_y(self, world_x):
        geo = self._get_geometry(self.rect)
        x = max(geo["left"], min(int(world_x), geo["right"] - 1))

        if geo["left_inner"] <= x < geo["right_inner"]:
            return geo["bottom_y"]

        if x < geo["left_inner"]:
            step_index = (x - geo["left"]) // geo["inset_per_step"]
        else:
            step_index = (geo["right"] - 1 - x) // geo["inset_per_step"]

        step_index = max(0, min(geo["steps"] - 1, step_index))
        return min(geo["bottom_y"], geo["top_y"] + step_index * geo["step_height"])

    def get_stair_index(self, world_x):
        geo = self._get_geometry(self.rect)

        x = max(geo["left"], min(int(world_x), geo["right"] - 1))

        if geo["left_inner"] <= x < geo["right_inner"]:
            return None

        if x < geo["left_inner"]:
            step_index = (x - geo["left"]) // geo["inset_per_step"]
        else:
            step_index = (geo["right"] - 1 - x) // geo["inset_per_step"]

        return max(0, min(geo["steps"] - 1, step_index))

    @staticmethod
    def _is_in_stair_zone_geo(geo, world_x):
        x = int(world_x)
        if x < geo["left"]:
            return True
        if x >= geo["right"]:
            return True
        return x < geo["left_inner"] or x >= geo["right_inner"]
 
    def get_stair_support_y_for_rect(self, rect, foot_padding=4):
        geo = self._get_geometry(self.rect)
 
        left_foot_x = rect.left + foot_padding
        right_foot_x = rect.right - foot_padding
        center_x = rect.centerx
 
        supports = []
        if self._is_in_stair_zone_geo(geo, left_foot_x):
            supports.append(self.get_stair_surface_y(left_foot_x))
        if self._is_in_stair_zone_geo(geo, right_foot_x):
            supports.append(self.get_stair_surface_y(right_foot_x))
 
        if len(supports) == 1 and not self._is_in_stair_zone_geo(geo, center_x):
            return None
 
        if not supports and self._is_in_stair_zone_geo(geo, center_x):
            supports.append(self.get_stair_surface_y(center_x))
 
        if not supports:
            return None
        return min(supports)

    def _build_left_earth_rects(self, geo):
        rects = []
        for i in range(geo["steps"]):
            lx = geo["left"] + i * geo["inset_per_step"]
            ly = min(geo["bottom_y"], geo["top_y"] + i * geo["step_height"])
            if i == geo["steps"] - 1:
                lw = geo["left_inner"] - lx
            else:
                lw = geo["inset_per_step"]
            lh = geo["bottom_y"] - ly
            if lw > 0 and lh > 0:
                rects.append(pygame.Rect(lx, ly, lw, lh))
        return rects

    def _build_right_earth_rects(self, geo):
        rects = []
        for i in range(geo["steps"]):
            ry = min(geo["bottom_y"], geo["top_y"] + i * geo["step_height"])
            if i == geo["steps"] - 1:
                rx = geo["right_inner"]
                rw = (geo["right"] - i * geo["inset_per_step"]) - rx
            else:
                rx = geo["right"] - (i + 1) * geo["inset_per_step"]
                rw = geo["inset_per_step"]
            rh = geo["bottom_y"] - ry
            if rw > 0 and rh > 0:
                rects.append(pygame.Rect(rx, ry, rw, rh))
        return rects

    def draw(self, surface, camera_x=0):
        self._load_tiles()
        draw_rect = self.rect.move(-camera_x, 0)
        geo = self._get_geometry(draw_rect)
        self._fill_rect_with_water_tiles(surface, draw_rect)
        for rect in self._build_left_earth_rects(geo):
            self._fill_rect_with_tiles(surface, rect)
        
        for rect in self._build_right_earth_rects(geo):
            self._fill_rect_with_tiles(surface, rect)