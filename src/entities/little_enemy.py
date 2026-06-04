import pygame
from pathlib import Path
from src.utils.config import PLAYER_SPEED
from src.entities.enemy import Enemy

class LittleEnemy(Enemy):
    ANIM_FPS = {"idle": 8, "attack": 4, "death": 8}
    _assets_loaded = False
    _frames = {"idle": [], "attack": [], "death": []}

    PATROL_DISTANCE = 120
    PATROL_SPEED    = PLAYER_SPEED * 0.5

    def __init__(self, pos, attacks=None):
        super().__init__(pos, attacks=attacks)
        self.draw_width  = 44
        self.draw_height = 44
        self.patrol_origin = pygame.Vector2(pos)
        self._load_assets()
        self._update_animation(0.0)

    @classmethod
    def _load_assets(cls):
        if cls._assets_loaded:
            return
        project_root = Path(__file__).resolve().parents[2]
        sprite_path = (
            project_root / "assets" / "sprites"
            / "brackeys_platformer_assets" / "sprites" / "slime_purple.png"
        )
        if not sprite_path.exists():
            cls._frames["idle"] = []
            cls._frames["attack"] = []
            cls._frames["death"] = []
            cls._assets_loaded = True
            return
        try:
            sheet = pygame.image.load(str(sprite_path)).convert_alpha()
            fw, fh = 24, 24
            cols = sheet.get_width() // fw
            rows = sheet.get_height() // fh

            all_frames = [
                sheet.subsurface(pygame.Rect(col * fw, row * fh, fw, fh)).copy()
                for row in range(rows)
                for col in range(cols)
            ]
            cls._frames["idle"]   = [f for i, f in enumerate(all_frames) if i != 10]
            cls._frames["attack"] = [all_frames[10]]
            cls._frames["death"] = [all_frames[10]]
        except pygame.error:
            cls._frames["idle"] = []
            cls._frames["attack"] = []
            cls._frames["death"] = []
        cls._assets_loaded = True

    def _on_update(self, dt, player):
        left_bound  = self.patrol_origin.x
        right_bound = self.patrol_origin.x + self.PATROL_DISTANCE

        if self.facing_right:
            self.vel.x = self.PATROL_SPEED
            if self.pos.x >= right_bound:
                self.facing_right = False
        else:
            self.vel.x = -self.PATROL_SPEED
            if self.pos.x <= left_bound:
                self.facing_right = True

        if (
            player
            and self.rect.colliderect(player.rect)
            and self.attack_cooldown == 0.0
        ):
            self._start_attack()
            self._deal_damage(player)

    def _start_attack(self):
        self.attack_timer    = 0.3
        self.attack_cooldown = self.attack_interval
        self.anim_state      = "attack"
        self.anim_time       = 0.0
        self.anim_index      = 0