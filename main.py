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

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    screen.fill(BLACK)
    pygame.draw.line(screen, GREEN, [0, 400], [640, 400], 5)
    pygame.draw.rect(screen, BROWN, [0, 400, 640, 80])
    pygame.draw.ellipse(screen, RED, [40, 360, 40, 40])

    pygame.display.flip()
pygame.quit()
exit()
