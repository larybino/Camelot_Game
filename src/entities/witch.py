import pygame
from pathlib import Path
from src.utils.config import PLAYER_SPEED
from src.entities.enemy import Enemy


class Witch(Enemy):
    ANIM_FPS = {"idle": 8, "attack": 6, "death": 8}
    _assets_loaded = False
    _frames = {"idle": [], "attack": [], "death": []}

    def __init__(self, pos, attacks=None):
        super().__init__(pos, attacks=attacks)
        self.draw_width  = 145
        self.draw_height = 145
        self._load_assets()
        self._update_animation(0.0)

    @classmethod
    def _load_assets(cls):
        if cls._assets_loaded:
            return
        project_root = Path(__file__).resolve().parents[2]
        sprite_map = {
            "idle":   "ArchDemonIdle001-Sheet.png",
            "attack": "ArchDemonBasicAtk001-Sheet.png",
            "death":  "ArchDemonDeath001-Sheet.png",
        }
        for state, filename in sprite_map.items():
            sprite_path = (
                project_root / "assets" / "sprites"
                / "duskBorne" / "SpriteSheets" / filename
            )
            if not sprite_path.exists():
                cls._frames[state] = []
                continue
            try:
                sheet = pygame.image.load(str(sprite_path)).convert_alpha()
                h = sheet.get_height()
                cls._frames[state] = [
                    sheet.subsurface(pygame.Rect(i * h, 0, h, h)).copy()
                    for i in range(sheet.get_width() // h)
                ]
            except pygame.error:
                cls._frames[state] = []
        cls._assets_loaded = True

    def _on_update(self, dt, player):
        if self.move_input:
            self.vel.x = PLAYER_SPEED * (1 if self.facing_right else -1)
        else:
            self.vel.x = 0

        if (
            player
            and abs(self.pos.x - player.pos.x) < self.attack_range_x
            and abs(self.pos.y - player.pos.y) < self.attack_range_y
            and self.attack_cooldown == 0.0
        ):
            self._start_attack()
            self._deal_damage(player)