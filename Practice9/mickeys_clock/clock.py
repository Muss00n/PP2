import pygame
import math
import datetime
import os
 
 
def draw_hand(surf, cx, cy, angle_rad, length, width, color):
    """Draw a clock hand with a rounded tip and drop shadow."""
    tip_x  = cx + length * math.cos(angle_rad)
    tip_y  = cy + length * math.sin(angle_rad)
    tail_l = length * 0.15
    tail_x = cx - tail_l * math.cos(angle_rad)
    tail_y = cy - tail_l * math.sin(angle_rad)
 
    pygame.draw.line(surf, (30, 30, 30),
                     (int(tail_x) + 3, int(tail_y) + 3),
                     (int(tip_x)  + 3, int(tip_y)  + 3), width + 2)
    pygame.draw.line(surf, color,
                     (int(tail_x), int(tail_y)),
                     (int(tip_x),  int(tip_y)), width)
    pygame.draw.circle(surf, color, (int(tip_x), int(tip_y)), width // 2)
 
 
class MickeyClock:
    def __init__(self, screen):
        self.screen = screen
        self.W, self.H = screen.get_size()
        self.cx = self.W // 2
        self.cy = self.H // 2
 
        img_path = os.path.join(os.path.dirname(__file__), "images", "mickeyclock.jpeg")
        raw = pygame.image.load(img_path).convert_alpha()
 
        dial_size   = min(self.W, self.H) - 20
        self.radius = dial_size // 2
 
        scaled = pygame.transform.smoothscale(raw, (dial_size, dial_size))
 
        self.face_surf = pygame.Surface((dial_size, dial_size), pygame.SRCALPHA)
        self.face_surf.fill((0, 0, 0, 0))
        mask = pygame.Surface((dial_size, dial_size), pygame.SRCALPHA)
        mask.fill((0, 0, 0, 0))
        pygame.draw.circle(mask, (255, 255, 255, 255),
                           (dial_size // 2, dial_size // 2), dial_size // 2)
        temp = scaled.copy()
        temp.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        self.face_surf = temp
        self.face_rect = self.face_surf.get_rect(center=(self.cx, self.cy))
 
        self.font_time = pygame.font.SysFont("Consolas", 32, bold=True)
        self.font_lbl  = pygame.font.SysFont("Arial", 17)
 
        self.C_MIN = (30,  30,  30)   
        self.C_SEC = (200, 30,  30)  
        self.C_BG  = (245, 245, 245)
 
        self.now = datetime.datetime.now()
 
    def update(self):
        self.now = datetime.datetime.now()
 
    def draw(self):
        self.screen.fill(self.C_BG)
 
        self.screen.blit(self.face_surf, self.face_rect)

        min_val = self.now.minute + self.now.second / 60.0
        min_ang = math.radians(min_val / 60 * 360 - 90)
 
        sec_val = self.now.second + self.now.microsecond / 1_000_000
        sec_ang = math.radians(sec_val / 60 * 360 - 90)
 
        draw_hand(self.screen, self.cx, self.cy,
                  min_ang, self.radius * 0.54, 7, self.C_MIN)
        draw_hand(self.screen, self.cx, self.cy,
                  sec_ang, self.radius * 0.68, 3, self.C_SEC)
 
        pygame.draw.circle(self.screen, (50,  50,  50),  (self.cx, self.cy), 9)
        pygame.draw.circle(self.screen, (220, 220, 220), (self.cx, self.cy), 4)
 
        self._draw_digital()
        self._draw_legend()
 
    def _draw_digital(self):
        time_str = self.now.strftime("%M:%S")
        txt  = self.font_time.render(time_str, True, (40, 40, 40))
        rect = txt.get_rect(center=(self.cx, self.cy + self.radius + 28))
        pad  = 12
        bg   = pygame.Rect(rect.left - pad, rect.top - 5,
                           rect.width + pad * 2, rect.height + 10)
        pygame.draw.rect(self.screen, (220, 220, 220), bg, border_radius=10)
        pygame.draw.rect(self.screen, (160, 160, 160), bg, 2, border_radius=10)
        self.screen.blit(txt, rect)
 
    def _draw_legend(self):
        items = [
            (self.C_MIN, "Right hand = Minutes"),
            (self.C_SEC, "Left hand  = Seconds"),
        ]
        x, y = 12, self.H - 56
        for color, label in items:
            pygame.draw.rect(self.screen, color, (x, y, 16, 16), border_radius=3)
            txt = self.font_lbl.render(label, True, (60, 60, 60))
            self.screen.blit(txt, (x + 24, y))
            y += 26
