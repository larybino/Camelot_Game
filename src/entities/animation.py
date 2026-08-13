import pygame
from .sprite import Sprite

class Animation:
    def __init__(
        self,
        sprites: list[Sprite],
        fps: int,
        draw_width: int,
        draw_height: int,
        loop: bool = True,
    ):
        self.sprites = sprites
        self.fps = fps
        self.draw_width = draw_width
        self.draw_height = draw_height
        self.loop = loop
        self.frame_duration = 1.0 / fps if fps > 0 else 0.0

        self._time = 0.0
        self._index = 0
        self.is_finished = False

    @classmethod
    def from_surfaces(
        cls,
        frames: list[pygame.Surface],
        fps: int,
        draw_width: int,
        draw_height: int,
        loop: bool = True,
    ) -> "Animation":
        return cls(
            sprites=[Sprite(frame) for frame in frames],
            fps=fps,
            draw_width=draw_width,
            draw_height=draw_height,
            loop=loop,
        )


    def update(self, dt: float) -> None:
        if not self.sprites or self.is_finished:
            return

        # Evita divisao por zero quando fps <= 0 (animacao fica no frame atual).
        if self.frame_duration <= 0.0:
            return

        self._time += dt
        if self._time < self.frame_duration:
            return

        frames_to_advance = int(self._time // self.frame_duration)
        self._time %= self.frame_duration
        self._index += frames_to_advance

        if self._index >= len(self.sprites):
            if self.loop:
                self._index %= len(self.sprites)
            else:
                self._index = len(self.sprites) - 1
                self.is_finished = True

    def reset(self) -> None:
        self._time = 0.0
        self._index = 0
        self.is_finished = False

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
        sprite = self.current_sprite
        if sprite is None:
            return

        sprite.draw(
            surface,
            x,
            y,
            draw_width=self.draw_width,
            draw_height=self.draw_height,
            flip_h=flip_h,
            char_width=char_width,
            char_height=char_height,
            y_offset=y_offset,
            foot_bonus=foot_bonus,
        )

    @property
    def current_sprite(self) -> Sprite | None:
        if not self.sprites:
            return None
        return self.sprites[self._index]