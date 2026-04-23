import random

from src.building.ladder import Ladder
from src.entities.artifact import Artifact
from src.building.platform import Platform
from src.entities.player import Player
from src.utils.config import GROUND_Y, SCREEN_H, SCREEN_W, WORLD_WIDTH, P_HEIGHT, P_WIDTH


class GameWorld:
    def __init__(self):
        self.platforms = self._build_platforms()
        self.ladders   = self._build_ladders()
        self.artifacts = self._build_artifacts()
        self.player    = self._build_player()
        self.camera_x  = 0.0
        self.player_spawn = self.player.pos.copy()
        self.death_y = 465

        self.active_objects = []
        self.active_objects.extend(self.artifacts)
        self.active_objects.append(self.player)

    def _build_platforms(self):
        platforms = []
        ground_y  = 400

        ground_segments = [
            (0,    2000),
            (2100, 1800),
            (4000, 2000),
        ]
        for start_x, width in ground_segments:
            platforms.append(Platform(start_x, ground_y, width, 80))

        floating = [
            (*self.generate_random_positions(), 120),
            (*self.generate_random_positions(), 100),
            (*self.generate_random_positions(), 130),
            (*self.generate_random_positions(), 110),
            (*self.generate_random_positions(), 110),
            (150, 256, 30),
            (250, 56, 110),
        ]
        for x, y, w in floating:
            platforms.append(Platform(x, y, w, 28))

        return platforms
    
    def _build_ladders(self):
        ladders = []
        ladder_positions = [
            (500, 200),
            (1000, 200),
            (1160, 190),
            (1300, 230),
        ]
        for x, y in ladder_positions:
            ladders.append(Ladder(x, y, 20, 100))

        return ladders

    def _build_player(self):
        return Player(60, 400 - P_HEIGHT)
    
    def _build_artifacts(self):
        return [
            Artifact("Excalibur", "power", 587, 240),
            Artifact("Santo Graal", "healing", *self.generate_random_positions()),
            Artifact("Cajado de Merlim", "magic", *self.generate_random_positions()),
        ]

    def _update_camera(self):
        target = self.player.pos.x - SCREEN_W // 2
        self.camera_x += (target - self.camera_x) * 0.15
        self.camera_x = max(0, min(self.camera_x, WORLD_WIDTH - SCREEN_W))

    def handle_event(self, event):
        for obj in self.active_objects:
            if obj.active:
                obj.handle_event(event, self)

    def _collect_artifacts(self):
        for artifact in self.artifacts[:]:
            if self.player.rect.colliderect(artifact.rect):
                self.player.artifacts.append(artifact)
                artifact.active = False
                self.artifacts.remove(artifact)
                if artifact in self.active_objects:
                    self.active_objects.remove(artifact)

    def update(self, dt):

        art_id = self.player.rect.collidelist(self.artifacts)
        if art_id != -1:
            self.player.artifacts.append(self.artifacts[art_id])
            del self.artifacts[art_id]

        lad_id =  self.player.rect.collidelist(self.ladders)
        if lad_id != -1:
            self.player.handle_ladders(dt, self.ladders[lad_id])
        else:
            self.player.update(dt, self.platforms)

        if self.player.pos.x < 0:
            self.player.pos.x = 0
        elif self.player.pos.x > WORLD_WIDTH - P_WIDTH:
            self.player.pos.x = WORLD_WIDTH - P_WIDTH

        if self.player.pos.y > 465:
            self.player.pos.x = 60
            self.player.pos.y = 320
        self._update_camera()   

    def draw(self, surface):
        cam = int(self.camera_x)
        for plat in self.platforms:
            plat.draw(surface, cam)
            if(plat.rect.top <= 305):
                height = (plat.rect.top - 266) * -1
                height = height if height > 50 else 50 
                plat_lad = Ladder(plat.rect.left -20, plat.rect.top, 20, height)
                plat_lad.draw(surface, cam)
                self.ladders.append(plat_lad)
        
        for ladder in self.ladders:
            ladder.draw(surface, cam)

        for obj in self.active_objects:
            if obj.active:
                obj.draw(surface, cam)

        for i, artifact in enumerate(self.player.artifacts):
            artifact.pos.x = 10 + i * 30
            artifact.pos.y = 55
            artifact.draw(surface, 0)
    
                    
    def get_artifact_info(self):
        if self.player.artifacts:
            return "Artifacts: "
        return "No artifacts collected"

    def generate_random_positions(self):
        x = random.randint(P_WIDTH, WORLD_WIDTH - P_WIDTH)
        y = random.randint(SCREEN_H - GROUND_Y , 360)
        return x, y
