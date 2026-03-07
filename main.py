import pygame
from pygame.locals import *
from sys import exit

pygame.init()

BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

screen = pygame.display.set_mode([640, 480])
pygame.display.set_caption('Camelot')

clock = pygame.time.Clock()

ground_y = 400
ground_height = 80

player_pos = pygame.Vector2(60, ground_y - 20) 
player_vel = pygame.Vector2(0, 0)
player_speed = 200  
gravity = 900       
jump_speed = -420
on_ground = True

obstacle_rect = pygame.Rect(200, 320, 200, 50)
obstacle_is_ground = False

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    dt = clock.tick(60) / 1000 

    keys = pygame.key.get_pressed()
    player_vel.x = 0
    if keys[K_LEFT] or keys[K_a]:
        player_vel.x = -player_speed
    if keys[K_RIGHT] or keys[K_d]:
        player_vel.x = player_speed
    if (keys[K_UP] or keys[K_w]) and on_ground:
        player_vel.y = jump_speed
        on_ground = False
        obstacle_is_ground = False

    player_vel.y += gravity * dt

    prev_pos = player_pos.copy()
    player_pos += player_vel * dt

    player_bottom = player_pos.y + 40 
    if player_bottom >= ground_y:
        player_pos.y = ground_y - 40
        player_vel.y = 0
        on_ground = True
        obstacle_is_ground = False

    player_rect = pygame.Rect(player_pos.x, player_pos.y, 40, 40)
    if player_rect.colliderect(obstacle_rect):
        if prev_pos.y + 40 <= obstacle_rect.top and player_vel.y > 0:
            player_pos.y = obstacle_rect.top - 40
            player_vel.y = 0
            on_ground = True
            obstacle_is_ground = True
        elif prev_pos.y >= obstacle_rect.bottom and player_vel.y < 0:
            player_pos.y = obstacle_rect.bottom
            player_vel.y = 0
        elif prev_pos.x + 40 <= obstacle_rect.left and player_vel.x > 0:
            player_pos.x = obstacle_rect.left - 40
        elif prev_pos.x >= obstacle_rect.right and player_vel.x < 0:
            player_pos.x = obstacle_rect.right

    if not (player_bottom >= ground_y or (player_rect.colliderect(obstacle_rect) and prev_pos.y + 40 <= obstacle_rect.top)):
        on_ground = False
        obstacle_is_ground = False
    screen.fill(BLACK)
    pygame.draw.line(screen, GREEN, [0, ground_y], [640, ground_y], 5)
    pygame.draw.rect(screen, BROWN, [0, ground_y, 640, ground_height])
    pygame.draw.ellipse(screen, RED, [player_pos.x, player_pos.y, 40, 40])

    pygame.draw.line(screen, GREEN, [200, 320], [400, 320], 5)
    pygame.draw.rect(screen, BROWN, obstacle_rect)

    pygame.display.flip()
pygame.quit()
exit()
