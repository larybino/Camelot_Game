import pygame

from src.menu.button import Button
from src.utils.config import SCREEN_W, SCREEN_H, WHITE, GOLD

CREDITS_LINES = [
    "Desenvolvimento",
    "Gregory e Laryssa",
    "",
    "Assets de sprites",
    "Brackeys Platformer Assets, DuskBorne, 16x16 RPG Item Pack",
    "",
    "Música e efeitos sonoros",
    "Pacotes de assets gratuitos utilizados no projeto",
    "",
    "Projeto acadêmico",
    "IFPR - Campus Paranavaí",
]


class CreditsScreen:
    def __init__(self, font, title_font):
        self.font = font
        self.title_font = title_font
        self.back_button = Button((SCREEN_W // 2 - 90, SCREEN_H - 60, 180, 40), "Voltar", font)

    def handle_event(self, event):
        if self.back_button.is_clicked(event):
            return "menu"
        return None

    def draw(self, surface):
        title = self.title_font.render("Créditos", True, GOLD)
        surface.blit(title, title.get_rect(center=(SCREEN_W // 2, 55)))

        heading_indices = {0, 3, 6, 9}
        y = 100
        for i, line in enumerate(CREDITS_LINES):
            color = GOLD if i in heading_indices else WHITE
            label = self.font.render(line, True, color)
            surface.blit(label, label.get_rect(center=(SCREEN_W // 2, y)))
            y += 22

        self.back_button.draw(surface)
