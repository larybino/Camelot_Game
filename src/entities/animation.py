import pygame

class Animation:
    def __init__(self, frames: list[pygame.Surface], fps: int, loop: bool = True):
        self.frames = frames
        self.fps = fps
        self.loop = loop
        self.frame_duration = 1.0 / fps if fps > 0 else 0.0

        self._time = 0.0
        self._index = 0
        self.is_finished = False


    def update(self, dt: float) -> None:
        if not self.frames or self.is_finished:
            return

        self._time += dt
        if self._time < self.frame_duration:
            return

        frames_to_advance = int(self._time // self.frame_duration)
        self._time %= self.frame_duration
        self._index += frames_to_advance

        if self._index >= len(self.frames):
            if self.loop:
                self._index %= len(self.frames)
            else:
                self._index = len(self.frames) - 1
                self.is_finished = True

    def reset(self) -> None:
        self._time = 0.0
        self._index = 0
        self.is_finished = False


    @property
    def current_frame(self) -> pygame.Surface | None:
        if not self.frames:
            return None
        return self.frames[self._index]