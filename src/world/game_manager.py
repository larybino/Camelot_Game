import pygame
from pygame.locals import QUIT
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
            if event.type == QUIT:
                self.running = False
            elif self.game_world is not None:
                self.game_world.handle_event(event)

    def _update(self, dt): 
        self.game_world.update(dt)

    def _render(self):
        self.screen.fill(BLACK)
        self.game_world.draw(self.screen)
        artifact_text = self.game_world.get_artifact_info()
        artifact_surface = self.font.render(artifact_text, True, WHITE)
        self.screen.blit(artifact_surface, (10, 30))
        pygame.display.flip()

    def quit(self):
        pygame.quit()