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
            if event.type == KEYDOWN and event.key == pygame.K_ESCAPE:
                # self.stopped = not self.stopped
                self.running = False
            if event.type == QUIT:
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

        if self.game_world is not None and self.game_world.game_over:
            message = "GAME OVER"
            text_surface = self.font.render(message, True, WHITE)
            text_rect = text_surface.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2))
            self.screen.blit(text_surface, text_rect)
        pygame.display.flip()

    def quit(self):
        pygame.quit()