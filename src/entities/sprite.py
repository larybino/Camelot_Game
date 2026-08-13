import pygame


class Sprite:
    def __init__(self, image: pygame.Surface):
        self.image = image
        self._foot_correction_cache: dict[int, int] = {}


    def draw(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        *,
        draw_width: int,
        draw_height: int,
        flip_h: bool = False,
        char_width: int = 0,
        char_height: int = 0,
        y_offset: int = 0,
        foot_bonus: int = 0,
    ) -> None:
        frame = self.image

        if flip_h:
            frame = pygame.transform.flip(frame, True, False)

        feet_correction = self._get_feet_correction(draw_height)

        scaled = pygame.transform.scale(frame, (draw_width, draw_height))
        sx = x + (char_width - draw_width) // 2
        sy = y + (char_height - draw_height) + y_offset + feet_correction + foot_bonus
        surface.blit(scaled, (sx, sy))

    def _get_feet_correction(self, draw_height: int) -> int:
        cached = self._foot_correction_cache.get(draw_height)
        if cached is not None:
            return cached

        reference_frame = self.image
        if reference_frame is None:
            self._foot_correction_cache[draw_height] = 0
            return 0

        bounds = reference_frame.get_bounding_rect(min_alpha=1)
        bottom_padding = max(0, reference_frame.get_height() - bounds.bottom)
        scale_y = draw_height / reference_frame.get_height()
        feet_correction = int(bottom_padding * scale_y)
        self._foot_correction_cache[draw_height] = feet_correction
        return feet_correction