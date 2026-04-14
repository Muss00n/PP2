import pygame
import sys
from ball import Ball
pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Moving Ball Game")

WHITE = (255, 255, 255)

ball = Ball(WIDTH, HEIGHT)
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                ball.move("UP")
            elif event.key == pygame.K_DOWN:
                ball.move("DOWN")
            elif event.key == pygame.K_LEFT:
                ball.move("LEFT")
            elif event.key == pygame.K_RIGHT:
                ball.move("RIGHT")

    screen.fill(WHITE)
    ball.draw(screen)
    
    pygame.display.flip()
    
    clock.tick(60)

pygame.quit()
sys.exit()