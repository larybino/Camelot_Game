import pygame
from pathlib import Path
from pygame.locals import QUIT, KEYDOWN
from src.utils.config import (SCREEN_W, SCREEN_H, FPS, BLACK, WHITE)
from src.world.game_world import GameWorld

class GameManager:
    def __init__(self):
        pygame.init()
        self.screen  = pygame.display.set_mode([SCREEN_W, SCREEN_H])
        pygame.display.set_caption('Camelot')
        self.clock   = pygame.time.Clock()
        self.font    = pygame.font.Font(None, 24)
        self.running = True
        self.game_world = None
        self.background = self._load_background()

    def _load_background(self):
        bg_path = Path(__file__).resolve().parents[2] / "assets" / "Background.png"
        if not bg_path.exists():
            return None

        try:
            bg = pygame.image.load(str(bg_path)).convert()
            return pygame.transform.scale(bg, (SCREEN_W, SCREEN_H))
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
        artifact_text = self.game_world.get_artifact_info()
        artifact_surface = self.font.render(artifact_text, True, WHITE)
        self.screen.blit(artifact_surface, (10, 30))
        pygame.display.flip()

    def quit(self):
        pygame.quit()