import pygame
from pathlib import Path

from src.utils.config import PLAYER_SPEED
from src.entities.enemy import Enemy
from src.entities.animation import Animation
from src.entities.sprite import Sprite
from src.entities.sprite_manager import SpriteManager


class LittleEnemy(Enemy):

    PATROL_DISTANCE = 120
    PATROL_SPEED    = PLAYER_SPEED * 0.5

    _frames_cache: dict[str, list[pygame.Surface]] | None = None

    def __init__(self, pos, attacks=None):
        super().__init__(pos, attacks=attacks)
        self.patrol_origin = pygame.Vector2(pos)
        self._load_animations()
        if self.sprite:
            self.sprite.set_animation("idle")

    def _load_animations(self) -> None:
        if LittleEnemy._frames_cache is None:
            root = Path(__file__).resolve().parents[2]
            path = (
                root / "assets" / "sprites"
                / "brackeys_platformer_assets" / "sprites" / "slime_purple.png"
            )
            if path.exists():
                all_frames = SpriteManager.load_grid(path, 24, 24)
                LittleEnemy._frames_cache = {
                    "idle":   [f for i, f in enumerate(all_frames) if i != 10],
                    "attack": [all_frames[10]],
                    "death":  [all_frames[10]],
                }
            else:
                LittleEnemy._frames_cache = {"idle": [], "attack": [], "death": []}

        f = LittleEnemy._frames_cache
        self.sprite = Sprite(
            animations={
                "idle":   Animation(f["idle"],   fps=8),
                "attack": Animation(f["attack"], fps=4,  loop=False),
                "death":  Animation(f["death"],  fps=8,  loop=False),
            },
            draw_width=44,
            draw_height=44,
        )

    def _logic_state_machine(self) -> None:
        if not self.sprite:
            return
        if self.is_dead:
            self.sprite.set_animation("death")
        elif self.attack_timer > 0:
            self.sprite.set_animation("attack")
        else:
            self.sprite.set_animation("idle")

    def _on_update(self, dt, player) -> None:
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

    def _start_attack(self) -> None:
        self.attack_timer    = 0.3
        self.attack_cooldown = self.attack_interval
        if self.sprite:
            self.sprite.set_animation("attack")