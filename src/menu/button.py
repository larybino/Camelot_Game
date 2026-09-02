import pygame


class Button:

    def __init__(self, rect, text, font, bg=(255, 255, 255), fg=(0, 0, 0), border=(0, 0, 0)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.bg = bg
        self.fg = fg
        self.border = border

    def is_clicked(self, event) -> bool:
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )

    def is_hovered(self) -> bool:
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def draw(self, surface):
        bg = self.bg
        if self.is_hovered():
            bg = tuple(max(0, c - 25) for c in self.bg)

        pygame.draw.rect(surface, bg, self.rect, border_radius=6)
        pygame.draw.rect(surface, self.border, self.rect, 2, border_radius=6)

        label = self.font.render(self.text, True, self.fg)
        surface.blit(label, label.get_rect(center=self.rect.center))
