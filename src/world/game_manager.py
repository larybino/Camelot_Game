import pygame
from pathlib import Path
from pygame.locals import QUIT, KEYDOWN
from src.utils.config import (SCREEN_W, SCREEN_H, FPS, BLACK, WHITE, RED)
from src.world.game_world import GameWorld

class GameManager:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen  = pygame.display.set_mode([SCREEN_W, SCREEN_H])
        pygame.display.set_caption('Camelot')
        self.clock   = pygame.time.Clock()
        self.font    = pygame.font.Font(None, 24)
        self.running = True
        self.game_world = None
        self.background = self._load_background()
        self.heart_sprite = self._load_heart_sprite()
        self.retry_button = pygame.Rect(SCREEN_W // 2 - 175, SCREEN_H // 2 + 40, 170, 40)
        self.exit_button = pygame.Rect(SCREEN_W // 2 + 15, SCREEN_H // 2 + 40, 120, 40 )

        music_path = Path(__file__).resolve().parents[2] / "assets" / "sprites" / "music" / "Flight_from_the_keep.mp3"
        if music_path.exists():
            pygame.mixer.music.load(str(music_path))
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)

    def _load_background(self):
        bg_path = Path(__file__).resolve().parents[2] / "assets" / "Background.png"
        if not bg_path.exists():
            return None

        try:
            bg = pygame.image.load(str(bg_path)).convert()
            return pygame.transform.scale(bg, (SCREEN_W, SCREEN_H))
        except pygame.error:
            return None

    def _load_heart_sprite(self):
        heart_path = Path(__file__).resolve().parents[2] / "assets" / "sprites" / "heart.png"
        if not heart_path.exists():
            return None

        try:
            heart = pygame.image.load(str(heart_path)).convert_alpha()
            return pygame.transform.scale(heart, (16, 16))
        except pygame.error:
            return None

    def start(self):
        self.game_world = GameWorld()
        self.main_loop()

    def main_loop(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0 
            self._handle_events()
            self._update(dt)
            self._render()
        self.quit() 

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key == pygame.K_m:
                    self.game_world.debug = not self.game_world.debug
            if event.type == QUIT:
                self.running = False

            if (
                self.game_world is not None
                and (self.game_world.game_over or self.game_world.game_won)
                and event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):
                if self.retry_button.collidepoint(event.pos):
                    self.game_world = GameWorld()

                elif self.exit_button.collidepoint(event.pos):
                    self.running = False

            elif self.game_world is not None:
                self.game_world.handle_event(event)

    def _update(self, dt): 
        self.game_world.update(dt)

    def _render(self):
        if self.background is not None:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(BLACK)
        self.game_world.draw(self.screen)

        if self.game_world is not None and self.game_world.player is not None:
            for i in range(self.game_world.player.lives):
                x = 10 + i * 20
                y = 6
                if self.heart_sprite is not None:
                    self.screen.blit(self.heart_sprite, (x, y))
                else:
                    pygame.draw.circle(self.screen, RED, (x + 6, y + 6), 6)
                    pygame.draw.circle(self.screen, WHITE, (x + 6, y + 6), 6, 1)

        artifact_text = self.game_world.get_artifact_info()
        artifact_surface = self.font.render(artifact_text, True, WHITE)
        self.screen.blit(artifact_surface, (10, 30))

        score_text = self.game_world.get_score_text()
        score_surface = self.font.render(score_text, True, WHITE)
        self.screen.blit(score_surface, (10, 50))

        if self.game_world is not None and (self.game_world.game_over or self.game_world.game_won):

            overlay = pygame.Surface((SCREEN_W, SCREEN_H))
            overlay.set_alpha(150)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            message = "YOU WIN" if self.game_world.game_won else "GAME OVER"
            text_surface = self.font.render(message, True, WHITE)
            text_rect = text_surface.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2))
            self.screen.blit(text_surface, text_rect)

            final_score = self.font.render(f"Final Score: {self.game_world.score}", True, WHITE)
            final_rect = final_score.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 24))
            self.screen.blit(final_score, final_rect)

            pygame.draw.rect(self.screen, WHITE, self.retry_button)
            pygame.draw.rect(self.screen, BLACK, self.retry_button, 2)

            retry_text = self.font.render("Tentar novamente?", True, BLACK)
            retry_rect = retry_text.get_rect(center=self.retry_button.center)
            self.screen.blit(retry_text, retry_rect)

            pygame.draw.rect(self.screen, WHITE, self.exit_button)
            pygame.draw.rect(self.screen, BLACK, self.exit_button, 2)

            exit_text = self.font.render("Sair", True, BLACK)
            exit_rect = exit_text.get_rect(center=self.exit_button.center)
            self.screen.blit(exit_text, exit_rect)

        pygame.display.flip()

    def quit(self):
        pygame.quit()