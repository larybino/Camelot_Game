import pygame

from src.menu.button import Button
from src.utils.config import SCREEN_W, SCREEN_H, WHITE, GOLD


class ScoreboardScreen:
    def __init__(self, font, title_font):
        self.font = font
        self.title_font = title_font
        self.back_button = Button((SCREEN_W // 2 - 90, SCREEN_H - 60, 180, 40), "Voltar", font)

    def handle_event(self, event):
        if self.back_button.is_clicked(event):
            return "menu"
        return None

    def draw(self, surface, scores):
        title = self.title_font.render("Placar", True, GOLD)
        surface.blit(title, title.get_rect(center=(SCREEN_W // 2, 60)))

        if not scores:
            empty = self.font.render("Nenhuma pontuação registrada ainda.", True, WHITE)
            surface.blit(empty, empty.get_rect(center=(SCREEN_W // 2, 160)))
        else:
            header = self.font.render(f"{'#':<4}{'Nome':<18}{'Pontos'}", True, GOLD)
            surface.blit(header, (SCREEN_W // 2 - 140, 105))

            for i, entry in enumerate(scores[:10]):
                name = entry.get("name", "Jogador")
                score = entry.get("score", 0)
                line = f"{i + 1:<4}{name:<18}{score}"
                color = GOLD if i == 0 else WHITE
                row = self.font.render(line, True, color)
                surface.blit(row, (SCREEN_W // 2 - 140, 132 + i * 26))

        self.back_button.draw(surface)
