import pygame
import sys
import os
from player import MusicPlayer

pygame.init()
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Music Player")
font = pygame.font.SysFont("Arial", 24)
clock = pygame.time.Clock()

base_path = os.path.dirname(os.path.abspath(__file__))
music_dir = os.path.join(base_path, 'music')
player = MusicPlayer(music_dir)

def draw_text(text, x, y, color=(255, 255, 255)):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

running = True
while running:
    screen.fill((30, 30, 30)) 

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p: player.play()
            elif event.key == pygame.K_s: player.stop()
            elif event.key == pygame.K_n: player.next_track()
            elif event.key == pygame.K_b: player.prev_track()
            elif event.key == pygame.K_q: running = False

    draw_text("Controls: P (Play), S (Stop), N (Next), B (Back), Q (Quit)", 20, 20, (150, 150, 150))
    
    status = "Playing" if player.is_playing else "Stopped"
    draw_text(f"Status: {status}", 20, 80)
    draw_text(f"Current Track: {player.get_current_track_name()}", 20, 120, (0, 255, 127))
    
    pos = player.get_progress()
    draw_text(f"Position: {pos // 60:02d}:{pos % 60:02d}", 20, 160)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()