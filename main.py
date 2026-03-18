import pygame
from pygame.locals import *
from sys import exit

pygame.init()

font = pygame.font.Font(None, 24)

FPS= 60
SCREEN_W= 640
SCREEN_H = 480
BLACK = (0, 0, 0)
BLUE = (30,  60, 120)
BROWN = (139, 69, 19)
GREEN = (0, 255, 0)
GREY = (120,110, 100)
WHITE= (255, 255, 255)
RED = (255, 0, 0)
PLAYER_SPEED = 200  
GRAVITY = 900       
JUMP_SPEED = -420
WIDTH  = 40
HEIGHT = 40

screen = pygame.display.set_mode([SCREEN_W, SCREEN_H])
pygame.display.set_caption('Camelot')

clock = pygame.time.Clock()

ground_y = 400

player_pos = pygame.Vector2(60, ground_y - 20) 
player_vel = pygame.Vector2(0, 0)

on_ground = True

class Platform:
    def __init__(self, x, y, width, height):
        self.rect        = pygame.Rect(x, y, width, height)
        self.color       = BROWN if height >= 40 else GREY
        self.grass_color = GREEN

    def draw(self, surface, parallax_factor=0):
        draw_rect = self.rect.move(-parallax_factor, 0)
        pygame.draw.rect(surface, self.color, draw_rect)
        grass_rect = pygame.Rect(draw_rect.x, draw_rect.y - 10, draw_rect.width, 10)
        pygame.draw.rect(surface, self.grass_color, grass_rect)

class Player:
    def __init__(self, x, y):
        self.pos       = pygame.Vector2(x, y)
        self.vel       = pygame.Vector2(0, 0)
        self.on_ground = False
    @property
    def rect(self):
        return pygame.Rect(int(self.pos.x), int(self.pos.y),
                           WIDTH, HEIGHT)
 
    def handle_input(self):
        keys = pygame.key.get_pressed()
 
        self.vel.x = 0
        if keys[K_LEFT] or keys[K_a]:
            if keys[K_RCTRL] or keys[K_LCTRL]:
                self.vel.x = -PLAYER_SPEED * 2
            else:
                self.vel.x = -PLAYER_SPEED
        if keys[K_RIGHT] or keys[K_d]:
            if keys[K_RCTRL] or keys[K_LCTRL]:
                self.vel.x = PLAYER_SPEED * 2
            else:
                self.vel.x = PLAYER_SPEED
        if (keys[K_UP] or keys[K_w] or keys[K_SPACE]) and self.on_ground:
            self.vel.y = JUMP_SPEED
            self.on_ground = False
 
    def update(self, dt, platforms):
        self.vel.y += GRAVITY * dt
 
        prev_pos = self.pos.copy()
 
        self.pos.x += self.vel.x * dt
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel.x > 0:                          
                    self.pos.x = plat.rect.left - WIDTH
                elif self.vel.x < 0:                        
                    self.pos.x = plat.rect.right
                self.vel.x = 0
 
        self.on_ground = False
        self.pos.y += self.vel.y * dt
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel.y > 0:                         
                    self.pos.y = plat.rect.top - HEIGHT
                    self.vel.y = 0
                    self.on_ground = True
                elif self.vel.y < 0:                       
                    self.pos.y = plat.rect.bottom
                    self.vel.y = 0
 
    def draw(self, surface, camera_x):
        draw_x = int(self.pos.x) - camera_x
        draw_y = int(self.pos.y)
        pygame.draw.ellipse(surface, RED,
                            (draw_x, draw_y, WIDTH, HEIGHT))
        pygame.draw.ellipse(surface, WHITE,
                            (draw_x, draw_y, WIDTH, HEIGHT), 2)


def build_platforms():
    platforms = []
    ground_y = 400
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
        (2020, 270, 80),    
        (2120, 310, 120),

        (2400, 340, 130),
        (2600, 280, 100),
        (2800, 330, 140),

        (3200, 300, 90),
        (3370, 240, 90),
        (3540, 300, 90),
        (3720, 360, 110),
    ]
    for x, y, w in floating:
        platforms.append(Platform(x, y, w, 18))
    return platforms

def update_parallax(parallax_factor, player_x, world_width):
    target = player_x - SCREEN_W // 2
    parallax_factor += (target - parallax_factor) * 0.15
    parallax_factor = max(0, min(parallax_factor, world_width - SCREEN_W))
    return parallax_factor

platforms = build_platforms()

deslocate  = 0.0
player= Player(60, ground_y - HEIGHT)
WORLD_WIDTH = 6000
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    dt = clock.tick(FPS) / 1000
    screen.fill(BLACK)
    player.handle_input()
    player.update(dt, platforms)
    if player.pos.x < 0:
            player.pos.x = 0
    deslocate = update_parallax(deslocate, player.pos.x, WORLD_WIDTH)

    for plat in platforms:
        plat.draw(screen, int(deslocate))
    player.draw(screen, int(deslocate))
 
    info = font.render(
        f"X: {int(player.pos.x)}   Y: {int(player.pos.y)}"
        f"   cam: {int(deslocate)}   {'NO CHÃO' if player.on_ground else 'no ar'}",
        True, WHITE
    )
    screen.blit(info, (10, 10))    
    pygame.display.flip()

pygame.quit()
exit()
