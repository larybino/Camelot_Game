import pygame

from src.menu.button import Button
from src.menu.text_input import TextInput
from src.utils.config import SCREEN_W, SCREEN_H, WHITE, GOLD


class EndScreen:


    def __init__(self, font, title_font, won, score, last_name=""):
        self.font = font
        self.title_font = title_font
        self.won = won
        self.score = score
        self.saved = False

        self.name_input = TextInput((SCREEN_W // 2 - 110, 230, 220, 36), font, initial_text=last_name)
        self.save_button = Button((SCREEN_W // 2 - 175, 288, 170, 40), "Salvar Pontuação", font)
        self.menu_button = Button((SCREEN_W // 2 + 15, 288, 160, 40), "Voltar ao Menu", font)

    def handle_event(self, event):
        self.name_input.handle_event(event)

        if self.save_button.is_clicked(event):
            return ("save", self.name_input.text)
        if self.menu_button.is_clicked(event):
            return ("menu", self.name_input.text)
        return None

    def mark_saved(self):
        self.saved = True

    def update(self, dt):
        self.name_input.update(dt)

    def draw(self, surface):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H))
        overlay.set_alpha(160)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))

        message = "VOCÊ VENCEU!" if self.won else "GAME OVER"
        color = GOLD if self.won else (255, 90, 90)
        title = self.title_font.render(message, True, color)
        surface.blit(title, title.get_rect(center=(SCREEN_W // 2, 110)))

        score_label = self.font.render(f"Pontuação final: {self.score}", True, WHITE)
        surface.blit(score_label, score_label.get_rect(center=(SCREEN_W // 2, 152)))

        name_label = self.font.render("Seu nome:", True, WHITE)
        surface.blit(name_label, (SCREEN_W // 2 - 110, 205))
        self.name_input.draw(surface)

        self.save_button.text = "Pontuação salva!" if self.saved else "Salvar Pontuação"
        self.save_button.draw(surface)
        self.menu_button.draw(surface)
