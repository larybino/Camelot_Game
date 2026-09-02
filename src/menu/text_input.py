import pygame


class TextInput:

    def __init__(self, rect, font, initial_text="", max_length=16):
        self.rect = pygame.Rect(rect)
        self.font = font
        self.text = initial_text
        self.max_length = max_length
        self.active = True
        self._cursor_timer = 0.0
        self._cursor_visible = True

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            return

        if event.type != pygame.KEYDOWN or not self.active:
            return

        if event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_TAB):
            self.active = False
        elif event.unicode and event.unicode.isprintable() and len(self.text) < self.max_length:
            self.text += event.unicode

    def update(self, dt):
        self._cursor_timer += dt
        if self._cursor_timer >= 0.5:
            self._cursor_timer = 0.0
            self._cursor_visible = not self._cursor_visible

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 255, 255), self.rect, border_radius=4)
        border_color = (255, 215, 0) if self.active else (60, 60, 60)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=4)

        display_text = self.text
        if self.active and self._cursor_visible:
            display_text += "|"

        label = self.font.render(display_text, True, (0, 0, 0))
        surface.blit(
            label,
            (self.rect.x + 8, self.rect.y + (self.rect.height - label.get_height()) // 2),
        )
