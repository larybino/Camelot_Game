import pygame
from pathlib import Path
from src.utils.config import PLAYER_SPEED
from src.entities.enemy import Enemy
from src.entities.animation import Animation
from src.entities.sprite_manager import SpriteManager

class Witch(Enemy):

    _frames_cache: dict[str, list[pygame.Surface]] | None = None

    def __init__(self, pos, attacks=None):
        super().__init__(
            pos,
            attacks=attacks,
            max_lives=3,
            attack_interval=2.0,     
            attack_range_x=110,      
            attack_range_y=80,
        )
        self._load_animations()
        self.set_animation("idle")

    def _load_animations(self) -> None:
        if Witch._frames_cache is None:
            root = Path(__file__).resolve().parents[2]
            base = root / "assets" / "sprites" / "duskBorne" / "SpriteSheets"
            sprite_map = {
                "idle":   "ArchDemonIdle001-Sheet.png",
                "attack": "ArchDemonBasicAtk001-Sheet.png",
                "death":  "ArchDemonDeath001-Sheet.png",
            }
            Witch._frames_cache = {}
            for state, filename in sprite_map.items():
                path = base / filename
                if path.exists():
                    sheet = SpriteManager._get_sheet(path)
                    if sheet:
                        h = sheet.get_height()
                        frames = SpriteManager.load_strip(path, h)
                        Witch._frames_cache[state] = [
                            frame for frame in frames
                            if frame.get_bounding_rect(min_alpha=1).width > 0
                        ]
                    else:
                        Witch._frames_cache[state] = []
                else:
                    Witch._frames_cache[state] = []

        f = Witch._frames_cache
        self.animations = {
            "idle":   Animation.from_surfaces(f["idle"],   fps=8,  draw_width=145, draw_height=145, loop=True),
            "attack": Animation.from_surfaces(f["attack"], fps=10, draw_width=145, draw_height=145, loop=False),
            "death":  Animation.from_surfaces(f["death"],  fps=8,  draw_width=145, draw_height=145, loop=False),
        }
        self._set_first_animation()

    def _on_update(self, dt, player) -> None:
        if self.is_attacking or not self.is_alive:
            self.vel.x = 0
            return

        self.vel.x = PLAYER_SPEED * (1 if self.facing_right else -1) if self.move_input else 0

        if player:
            dist_x = player.pos.x - self.pos.x
            if abs(dist_x) < 250:
                self.facing_right = dist_x > 0

            if (
                abs(dist_x) < self.attack_range_x
                and abs(self.pos.y - player.pos.y) < self.attack_range_y
                and self.attack_cooldown == 0.0
                and not self.is_attacking
            ):
                self._start_attack()
                self._deal_damage(player)