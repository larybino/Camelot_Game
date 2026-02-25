import pygame
from pygame.locals import *
from sys import exit

pygame.init()
screen = pygame.display.set_mode([640, 480])
pygame.display.set_caption('Camelot')
screen.fill([0, 0, 0])
pygame.display.flip()

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
pygame.quit()
exit()
