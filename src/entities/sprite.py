import pygame
from .animation import Animation


class Sprite:
    def __init__(
        self,
        animations: dict[str, Animation],
        draw_width: int,
        draw_height: int,
    ):
        self.animations = animations
        self.draw_width = draw_width
        self.draw_height = draw_height

        self._current_key: str = ""
        self._set_first_available()


    def set_animation(self, key: str) -> None:
        if key == self._current_key or key not in self.animations:
            return
        self._current_key = key
        self.animations[key].reset()

    @property
    def current_animation(self) -> Animation | None:
        return self.animations.get(self._current_key)

    @property
    def is_finished(self) -> bool:
        anim = self.current_animation
        return anim is not None and anim.is_finished


    def update(self, dt: float) -> None:
        anim = self.current_animation
        if anim:
            anim.update(dt)


    def draw(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        *,
        flip_h: bool = False,
        char_width: int = 0,
        char_height: int = 0,
        y_offset: int = 0,
        foot_bonus: int = 0,
    ) -> None:

        anim = self.current_animation
        if anim is None:
            return

        frame = anim.current_frame
        if frame is None:
            return

        if flip_h:
            frame = pygame.transform.flip(frame, True, False)

        bounds = frame.get_bounding_rect(min_alpha=1)
        bottom_padding = max(0, frame.get_height() - bounds.bottom)
        scale_y = self.draw_height / frame.get_height()
        feet_correction = int(bottom_padding * scale_y)

        scaled = pygame.transform.scale(frame, (self.draw_width, self.draw_height))
        sx = x + (char_width - self.draw_width) // 2
        sy = y + (char_height - self.draw_height) + y_offset + feet_correction + foot_bonus
        surface.blit(scaled, (sx, sy))


    def _set_first_available(self) -> None:
        first = next(iter(self.animations), None)
        if first:
            self._current_key = first