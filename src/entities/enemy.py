import pygame
from src.utils.config import RED, P_WIDTH, P_HEIGHT
from src.entities.character import Character
from src.world import collision


class Enemy(Character):

    DEATH_LINGER = 2.0

    def __init__(
        self,
        pos,
        attacks=None,
        max_lives=1,
        attack_interval=1.5,  # Aumentado para garantir que não corte animações longas
        attack_range_x=60,
        attack_range_y=40,
    ):
        super().__init__(
            pos,
            P_WIDTH,
            P_HEIGHT,
            RED,
            max_lives=max_lives,
            invuln_duration=0.0,
            attack_interval=attack_interval,
            attack_range_x=attack_range_x,
            attack_range_y=attack_range_y,
        )
        self.attacks = attacks or []
        self.death_timer = 0.0
        self.is_attacking = False  # Flag para evitar sobreposição de ataque

    def _apply_physics(self, dt, platforms) -> None:
        collision.apply_gravity(self, dt)
        collision.move_with_platforms(self, platforms, dt)

    def _logic_state_machine(self) -> None:
        if not self.animations:
            return

        if not self.is_alive:
            self.set_animation("death")
            return

        # BLINDAGEM DO ATAQUE:
        if self.is_attacking:
            current_anim = self.current_animation
            # Checamos se a animação de fato acabou no Animation.is_finished
            if current_anim and current_anim.is_finished:
                self.is_attacking = False
            else:
                # Garante que continua tocando o ataque sem tentar mudar de estado
                self.set_animation("attack")
                return

        self.set_animation("idle")

    def update(self, dt: float, platforms, player=None) -> None:
        if not self.is_alive:
            self.death_timer -= dt
            if self.death_timer <= 0.0:
                self.active = False
            else:
                self._logic_state_machine()
                self._update_animation(dt)
            return

        self.update_common(dt)
        self._on_update(dt, player)
        self._logic_state_machine()
        self._update_animation(dt)
        self._apply_physics(dt, platforms)

    def _on_update(self, dt, player) -> None:
        pass

    def _start_attack(self) -> None:
        super()._start_attack()
        self.is_attacking = True
        
        anim = self.animations.get("attack")

        duration = (len(anim.sprites) / anim.fps) if (anim and anim.sprites and anim.fps > 0) else 0.5
        self.attack_timer = duration
        
        self.attack_cooldown = max(self.attack_interval, duration + 0.3)

        self.set_animation("attack")

    def _deal_damage(self, target) -> None:
        if self.attacks:
            self.attacks[0](self, target)
        elif hasattr(target, "take_damage"):
            target.take_damage(1)

    def take_damage(self, amount=1, ignore_invuln=False):
        if super().take_damage(amount, ignore_invuln=True):
            if self.lives == 0:
                self.is_alive = False
                self.death_timer = self.DEATH_LINGER
                self.vel.x = 0
                self.vel.y = 0
            return True
        return False