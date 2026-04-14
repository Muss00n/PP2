import pygame
from clock import MickeyClock
 
def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    pygame.display.set_caption("Mickey's Clock")
    clock_app = MickeyClock(screen)
    fps = pygame.time.Clock()
 
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
 
        clock_app.update()
        clock_app.draw()
        pygame.display.flip()
        fps.tick(60)
 
    pygame.quit()
 
if __name__ == "__main__":
    main()