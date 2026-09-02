from tkinter import Button

import pygame
from src.menu.button import Button
from src.utils.config import SCREEN_W, WHITE, GOLD


class MainMenu:
    def __init__(self, font, title_font):
        self.font = font
        self.title_font = title_font

        cx = SCREEN_W // 2
        w, h, gap = 220, 44, 14
        start_y = 190

        self.buttons = {
            "play": Button((cx - w // 2, start_y, w, h), "Iniciar Jogo", font),
            "scores": Button((cx - w // 2, start_y + (h + gap), w, h), "Placar", font),
            "credits": Button((cx - w // 2, start_y + 2 * (h + gap), w, h), "Créditos", font),
            "exit": Button((cx - w // 2, start_y + 3 * (h + gap), w, h), "Sair", font),
        }

    def handle_event(self, event):
        for action, button in self.buttons.items():
            if button.is_clicked(event):
                return action
        return None

    def draw(self, surface):
        title = self.title_font.render("CAMELOT", True, GOLD)
        surface.blit(title, title.get_rect(center=(SCREEN_W // 2, 110)))

        subtitle = self.font.render("Uma aventura pelo reino", True, WHITE)
        surface.blit(subtitle, subtitle.get_rect(center=(SCREEN_W // 2, 150)))

        for button in self.buttons.values():
            button.draw(surface)
