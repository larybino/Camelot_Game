import pygame
from pathlib import Path
from src.utils.config import PLAYER_SPEED
from src.entities.enemy import Enemy
from src.entities.animation import Animation
from src.entities.sprite import Sprite
from src.entities.sprite_manager import SpriteManager

class Witch(Enemy):

    _frames_cache: dict[str, list[pygame.Surface]] | None = None

    def __init__(self, pos, attacks=None):
        super().__init__(pos, attacks=attacks)
        self._load_animations()
        if self.sprite:
            self.sprite.set_animation("idle")

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
                        Witch._frames_cache[state] = SpriteManager.load_strip(path, h)
                    else:
                        Witch._frames_cache[state] = []
                else:
                    Witch._frames_cache[state] = []

        f = Witch._frames_cache
        self.sprite = Sprite(
            animations={
                "idle":   Animation(f["idle"],   fps=8),
                "attack": Animation(f["attack"], fps=6, loop=False),
                "death":  Animation(f["death"],  fps=8, loop=False),
            },
            draw_width=145,
            draw_height=145,
        )

    def _on_update(self, dt, player) -> None:
        self.vel.x = PLAYER_SPEED * (1 if self.facing_right else -1) if self.move_input else 0

        if (
            player
            and abs(self.pos.x - player.pos.x) < self.attack_range_x
            and abs(self.pos.y - player.pos.y) < self.attack_range_y
            and self.attack_cooldown == 0.0
        ):
            self._start_attack()
            self._deal_damage(player)