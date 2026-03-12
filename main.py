import pygame
from pygame.locals import *
from sys import exit

pygame.init()

FPS= 60
SCREEN_W= 640
SCREEN_H = 480
BLACK = (0, 0, 0)
BLUE = (30,  60, 120)
BROWN = (139, 69, 19)
GREEN = (0, 255, 0)
GREY = (120,110, 100)
RED = (255, 0, 0)
player_speed = 200  
gravity = 900       
jump_speed = -420

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
WORLD_WIDTH = 6000
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    dt = clock.tick(FPS) / 1000

    keys = pygame.key.get_pressed()
    player_vel.x = 0
    if keys[K_LEFT] or keys[K_a]:
        if keys[K_RCTRL] or keys[K_LCTRL]:
            player_vel.x = -player_speed * 2
        else:
            player_vel.x = -player_speed

    if keys[K_RIGHT] or keys[K_d]:
        if keys[K_RCTRL] or keys[K_LCTRL]:
            player_vel.x = player_speed * 2
        else:
            player_vel.x = player_speed
    if (keys[K_UP] or keys[K_w]) and on_ground:
        player_vel.y = jump_speed
        on_ground = False

    player_vel.y += gravity * dt

    prev_pos = player_pos.copy()
    player_pos += player_vel * dt

    player_bottom = player_pos.y + 40
    player_rect = pygame.Rect(player_pos.x, player_pos.y, 40, 40)
    on_ground = False
    for plat in platforms:
        plat_rect = plat.rect
        if player_rect.colliderect(plat_rect):
            if prev_pos.y + 40 <= plat_rect.top and player_vel.y > 0:
                player_pos.y = plat_rect.top - 40
                player_vel.y = 0
                on_ground = True
            elif prev_pos.y >= plat_rect.bottom and player_vel.y < 0:
                player_pos.y = plat_rect.bottom
                player_vel.y = 0
            elif prev_pos.x + 40 <= plat_rect.left and player_vel.x > 0:
                player_pos.x = plat_rect.left - 40
            elif prev_pos.x >= plat_rect.right and player_vel.x < 0:
                player_pos.x = plat_rect.right
    if player_bottom >= ground_y:
        player_pos.y = ground_y - 40
        player_vel.y = 0
        on_ground = True
    screen.fill(BLACK)

    deslocate = update_parallax(deslocate, player_pos.x, WORLD_WIDTH)

    for plat in platforms:
        plat.draw(screen, int(deslocate))
    pygame.draw.ellipse(screen, RED, [player_pos.x - int(deslocate), player_pos.y, 40, 40])
    pygame.display.flip()

pygame.quit()
exit()
