import pygame
from pathlib import Path
from pygame.locals import QUIT, KEYDOWN
from src.utils.config import SCREEN_W, SCREEN_H, FPS, BLACK, WHITE, RED
from src.utils.scores import load_scores, save_score
from src.world.game_world import GameWorld
from src.menu.main_menu import MainMenu
from src.menu.scoreboard_screen import ScoreboardScreen
from src.menu.credits_screen import CreditsScreen
from src.menu.end_screen import EndScreen

class GameManager:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen  = pygame.display.set_mode([SCREEN_W, SCREEN_H])
        pygame.display.set_caption('Camelot')
        self.clock   = pygame.time.Clock()
        self.font    = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 48)
        self.running = True

        self.game_world = None
        self.background = self._load_background()
        self.heart_sprite = self._load_heart_sprite()

        self.last_player_name = ""
        self.state = "menu"  
        self.main_menu = MainMenu(self.font, self.title_font)
        self.scoreboard_screen = ScoreboardScreen(self.font, self.title_font)
        self.credits_screen = CreditsScreen(self.font, self.title_font)
        self.end_screen = None

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
        self.main_loop()

    def main_loop(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()
            self._update(dt)
            self._render()
        self.quit()

    def _start_new_game(self):
        self.game_world = GameWorld()
        self.end_screen = None
        self.state = "playing"


    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
                continue

            if event.type == KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.state in ("playing", "scores", "credits"):
                    self.state = "menu"
                elif self.state == "menu":
                    self.running = False
                continue

            if self.state == "menu":
                self._handle_menu_event(event)
            elif self.state == "playing":
                self._handle_playing_event(event)
            elif self.state == "end":
                self._handle_end_event(event)
            elif self.state == "scores":
                if self.scoreboard_screen.handle_event(event) == "menu":
                    self.state = "menu"
            elif self.state == "credits":
                if self.credits_screen.handle_event(event) == "menu":
                    self.state = "menu"

    def _handle_menu_event(self, event):
        action = self.main_menu.handle_event(event)
        if action == "play":
            self._start_new_game()
        elif action == "scores":
            self.state = "scores"
        elif action == "credits":
            self.state = "credits"
        elif action == "exit":
            self.running = False

    def _handle_playing_event(self, event):
        if event.type == KEYDOWN and event.key == pygame.K_m:
            self.game_world.debug = not self.game_world.debug
        self.game_world.handle_event(event)

    def _handle_end_event(self, event):
        if self.end_screen is None:
            return

        result = self.end_screen.handle_event(event)
        if result is None:
            return

        action, name = result
        self.last_player_name = name or self.last_player_name

        if action == "save":
            save_score(name, self.game_world.score)
            self.end_screen.mark_saved()
        elif action == "menu":
            if not self.end_screen.saved:
                save_score(name, self.game_world.score)
            self.end_screen = None
            self.game_world = None
            self.state = "menu"


    def _update(self, dt):
        if self.state == "playing":
            self.game_world.update(dt)
            if self.game_world.game_over or self.game_world.game_won:
                self.end_screen = EndScreen(
                    self.font,
                    self.title_font,
                    won=self.game_world.game_won,
                    score=self.game_world.score,
                    last_name=self.last_player_name,
                )
                self.state = "end"
        elif self.state == "end" and self.end_screen is not None:
            self.end_screen.update(dt)


    def _render(self):
        if self.background is not None:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(BLACK)

        if self.state == "menu":
            self.main_menu.draw(self.screen)

        elif self.state in ("playing", "end"):
            self.game_world.draw(self.screen)
            self._draw_hud()
            if self.state == "end" and self.end_screen is not None:
                self.end_screen.draw(self.screen)

        elif self.state == "scores":
            self.scoreboard_screen.draw(self.screen, load_scores())

        elif self.state == "credits":
            self.credits_screen.draw(self.screen)

        pygame.display.flip()

    def _draw_hud(self):
        if self.game_world is None or self.game_world.player is None:
            return

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

    def quit(self):
        pygame.quit()