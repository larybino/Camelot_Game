from src.building.ladder import Ladder
from src.entities.artifact import Artifact
from src.building.platform import Platform
from src.entities.player import Player
from src.utils.config import SCREEN_W, WORLD_WIDTH, P_HEIGHT, P_WIDTH


class GameWorld:
    def __init__(self):
        self.platforms = self._build_platforms()
        self.player    = self._build_player()
        self.artifacts = self._build_artifacts()
        self.ladders   = self._build_ladders()
        self.camera_x  = 0.0

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
            (350,  340, 120),
            (530,  280, 100),
            (700,  320, 130),

            (1000, 350, 110),
            (1160, 290, 110),
            (1320, 230, 110),

            (1900, 310, 120),
            (2020, 270,  80),
            (2120, 310, 120),

            (2400, 340, 130),
            (2600, 280, 100),
            (2800, 330, 140),

            (3200, 300,  90),
            (3370, 240,  90),
            (3540, 300,  90),
            (3720, 360, 110),
        ]
        for x, y, w in floating:
            platforms.append(Platform(x, y, w, 18))

        return platforms
    
    def _build_ladders(self):
        ladders = []
        ladder_positions = [
            (1000, 200, 20, 100),
            (1160, 190, 20, 100),
            (1300, 230, 20, 100),
        ]
        for x, y, width, height in ladder_positions:
            ladders.append(Ladder(x, y, width, height))

        return ladders

    def _build_player(self):
        return Player(60, 400 - P_HEIGHT)
    
    def _build_artifacts(self):
        return [
            Artifact("Excalibur", "power", 587, 240),
            Artifact("Santo Graal", "healing"),
            Artifact("Cajado de Merlim", "magic"),
        ]

    def _update_camera(self):
        target = self.player.pos.x - SCREEN_W // 2
        self.camera_x += (target - self.camera_x) * 0.15
        self.camera_x = max(0, min(self.camera_x, WORLD_WIDTH - SCREEN_W))

    def update(self, dt):
        self.player.handle_input()

        art_id = self.player.rect.collidelist(self.artifacts)
        if art_id != -1:
            self.player.artifacts.append(self.artifacts[art_id])
            del self.artifacts[art_id]

        if self.player.rect.collidelist(self.ladders) != -1:
            self.player.handle_ladders(dt)
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
        self.player.draw(surface, cam)
        for artifact in self.artifacts:
            artifact.draw(surface, cam, self.platforms)
        for ladder in self.ladders:
            ladder.draw(surface, cam)
        for artifact in self.player.artifacts:
            artifact.pos.x = 10 + self.player.artifacts.index(artifact) * 30
            artifact.pos.y = 55
            artifact.draw(surface, 0)
    
    def get_info_text(self):
        return (f"X: {int(self.player.pos.x)}   Y: {int(self.player.pos.y)}"
                f"   cam: {int(self.camera_x)}   "
                f"{'no chão' if self.player.on_ground else 'no ar'}")
                    
    def get_artifact_info(self):
        if self.player.artifacts:
            return "Artifacts: " + ", ".join([a.name for a in self.player.artifacts])
        return "No artifacts collected"